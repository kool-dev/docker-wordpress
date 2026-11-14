import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/publish.py"
spec = importlib.util.spec_from_file_location("publish", SCRIPT)
publish = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publish)


def records():
    return [
        dict(run="123", attempt="2", variant=v, arch=a,
             staging=f"{publish.REPOSITORY}:{publish.staging_tag('123', '2', v, a)}",
             digest=f"{publish.REPOSITORY}@sha256:{n:064x}")
        for n, (v, a) in enumerate(
            ((v, a) for v in publish.VARIANTS for a in publish.ARCHES), 1)
    ]


class PublicationTests(unittest.TestCase):
    def test_complete_plan(self):
        releases = publish.plan(records(), "123", "2")
        self.assertEqual(len(releases), 8)
        self.assertEqual([a for a, _ in releases[0][1]], ["amd64", "arm64"])

    def test_invalid_metadata(self):
        invalid = [[], records()[:-1], records() + [records()[0]]]
        for key, value in [
            ("run", "122"), ("attempt", "1"), ("variant", "8.5-nginx"),
            ("arch", "s390x"), ("staging", "foreign/wordpress:tag"),
            ("digest", "foreign/wordpress@sha256:" + "a" * 64),
            ("digest", publish.REPOSITORY + "@sha256:xyz"),
            ("digest", records()[1]["digest"]), ("digest", None),
        ]:
            changed = copy.deepcopy(records())
            changed[0][key] = value
            invalid.append(changed)
        changed = records()
        changed[0]["extra"] = "unexpected"
        invalid.append(changed)
        for case in invalid:
            with self.subTest(case=case), self.assertRaises(ValueError):
                publish.plan(case, "123", "2")

    def test_guard(self):
        base = dict(GITHUB_EVENT_NAME="push", GITHUB_REF="refs/heads/master",
                    GITHUB_REPOSITORY="kool-dev/docker-wordpress")
        for event in ("push", "repository_dispatch", "workflow_dispatch"):
            self.assertTrue(publish.trusted(dict(base, GITHUB_EVENT_NAME=event)))
        for override in (
            {"GITHUB_EVENT_NAME": "pull_request"},
            {"GITHUB_EVENT_NAME": "pull_request_target"},
            {"GITHUB_EVENT_NAME": "workflow_dispatch", "GITHUB_REF": "refs/heads/feature"},
            {"GITHUB_REPOSITORY": "fork/docker-wordpress"},
            {"GITHUB_REF": "refs/pull/1/merge"},
        ):
            env = dict(base, **override)
            self.assertFalse(publish.trusted(env))
            with patch.dict(publish.os.environ, env, clear=True), patch.object(publish, "docker") as docker:
                with self.assertRaises(ValueError):
                    publish.main()
                docker.assert_not_called()

    def test_remote_preflight_before_any_write(self):
        releases = publish.plan(records(), "123", "2")
        for bad in ("architecture", "index", "unavailable"):
            calls = []

            def docker(*args):
                calls.append(args)
                # Fail only on the final arm64 digest: no earlier stable writes allowed.
                last = releases[-1][1][-1][1] in args
                if bad == "unavailable" and last:
                    raise RuntimeError("registry unavailable")
                if "--raw" in args:
                    return json.dumps({"mediaType": "application/vnd.oci.image.index.v1+json"
                                       if bad == "index" and last else
                                       "application/vnd.oci.image.manifest.v1+json"})
                arch = next(a for _, images in releases for a, d in images if d in args)
                return json.dumps({"os": "linux", "architecture":
                                   "wrong" if bad == "architecture" and last else arch})

            with self.subTest(bad=bad), patch.object(publish, "docker", side_effect=docker):
                with self.assertRaises((ValueError, RuntimeError)):
                    publish.promote(releases)
                self.assertFalse(any("create" in c for c in calls))

    def test_exact_digest_promotion(self):
        releases = publish.plan(records(), "123", "2")

        def docker(*args):
            if "--raw" in args:
                return json.dumps({"mediaType": "application/vnd.oci.image.manifest.v1+json"})
            if "inspect" in args:
                arch = next(a for _, images in releases for a, d in images if d in args)
                return json.dumps({"os": "linux", "architecture": arch})
            return ""

        with patch.object(publish, "docker", side_effect=docker) as mock:
            publish.promote(releases)
        calls = [c.args for c in mock.call_args_list]
        self.assertEqual(len(calls), 40)
        self.assertTrue(all("inspect" in c for c in calls[:32]))
        self.assertEqual(calls[32:], [
            ("buildx", "imagetools", "create", "--tag", tag, *(d for _, d in images))
            for tag, images in releases])

    def test_stage_pushes_existing_local_image(self):
        env = dict(GITHUB_RUN_ID="123", GITHUB_RUN_ATTEMPT="2",
                   VARIANT="8.4-nginx", ARCH="arm64",
                   IMAGE="kooldev/wordpress:ci-wordpress-123-2-8.4-nginx-arm64")
        info = json.dumps([{"Os": "linux", "Architecture": "arm64", "Id": "tested-id"}])
        with patch.object(publish, "docker", side_effect=[
            info, "tag: digest: sha256:" + "a" * 64 + " size: 123", info
        ]) as docker, patch.object(publish.Path, "mkdir"), patch.object(publish.Path, "write_text") as write:
            publish.stage(env)
            self.assertEqual(docker.call_args_list[1].args, ("push", env["IMAGE"]))
            record = json.loads(write.call_args.args[0])
            self.assertEqual(record["digest"], publish.REPOSITORY + "@sha256:" + "a" * 64)
            self.assertFalse(any("build" in c.args for c in docker.call_args_list))


if __name__ == "__main__":
    unittest.main()
