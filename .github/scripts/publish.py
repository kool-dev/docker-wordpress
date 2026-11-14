"""Promote only this workflow attempt's complete set of native tested images."""

import json
import os
from pathlib import Path
import re
import subprocess
import sys


REPOSITORY = "kooldev/wordpress"
VARIANTS = tuple(f"{version}-nginx{suffix}"
                 for version in ("8.1", "8.2", "8.3", "8.4")
                 for suffix in ("", "-prod"))
ARCHES = ("amd64", "arm64")
DIGEST = re.compile(r"sha256:[0-9a-f]{64}")


def docker(*args):
    return subprocess.check_output(["docker", *args], text=True).strip()


def trusted(env):
    return (env.get("GITHUB_EVENT_NAME") in
            {"push", "workflow_dispatch", "repository_dispatch"}
            and env.get("GITHUB_REF") == "refs/heads/master"
            and env.get("GITHUB_REPOSITORY") == "kool-dev/docker-wordpress")


def staging_tag(run, attempt, variant, arch):
    return f"ci-wordpress-{run}-{attempt}-{variant}-{arch}"


def plan(records, run, attempt, repository=REPOSITORY):
    """Validate the entire set before performing any registry mutation."""
    if not re.fullmatch(r"[1-9][0-9]*", run) or not re.fullmatch(r"[1-9][0-9]*", attempt):
        raise ValueError("Invalid workflow run/attempt")
    found = {}
    digests = set()
    for record in records:
        if set(record) != {"run", "attempt", "variant", "arch", "staging", "digest"}:
            raise ValueError("Unexpected metadata fields")
        variant, arch = record["variant"], record["arch"]
        if variant not in VARIANTS or arch not in ARCHES:
            raise ValueError("Unknown variant/architecture")
        if record["run"] != run or record["attempt"] != attempt:
            raise ValueError("Metadata belongs to a different run/attempt")
        expected = f"{repository}:{staging_tag(run, attempt, variant, arch)}"
        if record["staging"] != expected:
            raise ValueError("Wrong staging repository/tag")
        digest = record["digest"]
        prefix = f"{repository}@"
        if not isinstance(digest, str) or not digest.startswith(prefix) or not DIGEST.fullmatch(digest[len(prefix):]):
            raise ValueError("Malformed or foreign repository digest")
        key = (variant, arch)
        if key in found or digest in digests:
            raise ValueError("Duplicate image metadata/digest")
        found[key] = digest
        digests.add(digest)
    if set(found) != {(v, a) for v in VARIANTS for a in ARCHES}:
        raise ValueError("Missing native image metadata")
    return [(f"{repository}:{v}", [(a, found[v, a]) for a in ARCHES])
            for v in VARIANTS]


def promote(releases):
    # Read every immutable manifest/config before changing even the first tag.
    # Reject indexes: staging must point to one native image, not another index.
    for _, images in releases:
        for arch, digest in images:
            manifest = json.loads(docker("buildx", "imagetools", "inspect", "--raw", digest))
            if manifest.get("mediaType") not in {
                "application/vnd.oci.image.manifest.v1+json",
                "application/vnd.docker.distribution.manifest.v2+json",
            }:
                raise ValueError("Staged digest is not a single image manifest")
            config = json.loads(docker("buildx", "imagetools", "inspect", digest,
                                       "--format", "{{json .Image}}"))
            if config.get("os") != "linux" or config.get("architecture") != arch:
                raise ValueError("Staged image architecture mismatch")
    for tag, images in releases:
        docker("buildx", "imagetools", "create", "--tag", tag,
               *(digest for _, digest in images))


def stage(env):
    run, attempt = env["GITHUB_RUN_ID"], env["GITHUB_RUN_ATTEMPT"]
    variant, arch = env["VARIANT"], env["ARCH"]
    image = env["IMAGE"]
    expected = f"{REPOSITORY}:{staging_tag(run, attempt, variant, arch)}"
    if variant not in VARIANTS or arch not in ARCHES or image != expected:
        raise ValueError("Unexpected local image")
    info = json.loads(docker("image", "inspect", image))[0]
    if (info["Os"], info["Architecture"]) != ("linux", arch):
        raise ValueError("Local image architecture mismatch")
    output = docker("push", image)
    matches = re.findall(r"digest: (sha256:[0-9a-f]{64})\b", output)
    if len(matches) != 1:
        raise ValueError("Push did not return exactly one repository digest")
    if json.loads(docker("image", "inspect", image))[0]["Id"] != info["Id"]:
        raise ValueError("Local image changed during push")
    record = dict(run=run, attempt=attempt, variant=variant, arch=arch,
                  staging=image, digest=f"{REPOSITORY}@{matches[0]}")
    Path("metadata").mkdir(exist_ok=True)
    Path(f"metadata/{variant}-{arch}.json").write_text(json.dumps(record) + "\n")


def main():
    # Defense in depth: direct script invocations cannot publish from PRs/forks.
    if not trusted(os.environ):
        raise ValueError("Publication requires the trusted repository's master branch")
    command = sys.argv[1]
    if command == "stage":
        stage(os.environ)
    elif command in {"preflight", "publish"}:
        records = [json.loads(p.read_text()) for p in Path("metadata").rglob("*.json")]
        releases = plan(records, os.environ["GITHUB_RUN_ID"], os.environ["GITHUB_RUN_ATTEMPT"])
        if command == "publish":
            promote(releases)
    else:
        raise ValueError("Unknown command")


if __name__ == "__main__":
    main()
