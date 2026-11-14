"""Opt-in real registry promotion test; no production credentials or images.

Run: python3 .github/tests/local_registry.py
Creates a temporary registry:2 container bound only to loopback and removes it
on exit. Uploads 16 distinct layerless (scratch) native manifests via Registry V2.
"""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_publication import publish  # noqa: E402


def request(url, method="GET", data=None, media=None):
    headers = {"Content-Type": media} if media else {}
    with urlopen(Request(url, data=data, method=method, headers=headers), timeout=15) as response:
        return response.headers, response.read()


def encode(value):
    return json.dumps(value, separators=(",", ":")).encode()


def digest(data):
    return "sha256:" + hashlib.sha256(data).hexdigest()


def main():
    container = subprocess.check_output([
        "docker", "create", "--publish", "127.0.0.1::5000", "registry:2"
    ], text=True).strip()
    try:
        subprocess.run(["docker", "start", container], check=True, stdout=subprocess.DEVNULL)
        port = subprocess.check_output(["docker", "port", container, "5000/tcp"], text=True).strip()
        base = f"http://{port}"
        for _ in range(100):
            try:
                request(base + "/v2/")
                break
            except OSError:
                time.sleep(0.1)
        repo = f"{port}/test/wordpress"
        api = base + "/v2/test/wordpress"
        records = []
        for variant in publish.VARIANTS:
            for arch in publish.ARCHES:
                config = encode({
                    "architecture": arch, "os": "linux",
                    "config": {"Labels": {"variant": variant}},
                    "rootfs": {"type": "layers", "diff_ids": []},
                })
                headers, _ = request(api + "/blobs/uploads/", "POST", b"")
                upload = headers["Location"]
                request(upload + "&digest=" + digest(config), "PUT", config,
                        "application/octet-stream")
                manifest = encode({
                    "schemaVersion": 2,
                    "mediaType": "application/vnd.oci.image.manifest.v1+json",
                    "config": {"mediaType": "application/vnd.oci.image.config.v1+json",
                               "size": len(config), "digest": digest(config)},
                    "layers": [],
                })
                tag = publish.staging_tag("123", "2", variant, arch)
                request(api + "/manifests/" + tag, "PUT", manifest,
                        "application/vnd.oci.image.manifest.v1+json")
                records.append(dict(run="123", attempt="2", variant=variant, arch=arch,
                                    staging=repo + ":" + tag,
                                    digest=repo + "@" + digest(manifest)))
        releases = publish.plan(records, "123", "2", repository=repo)
        publish.promote(releases)
        for tag, images in releases:
            index = json.loads(publish.docker("buildx", "imagetools", "inspect", "--raw", tag))
            actual = {(m["platform"]["architecture"], repo + "@" + m["digest"])
                      for m in index["manifests"]}
            assert actual == set(images), (tag, actual, images)
            assert len(index["manifests"]) == 2
        print("PASS: real local registry promoted 8 tags with exact 16 native scratch digests")
    finally:
        subprocess.run(["docker", "rm", "--force", container], check=True,
                       stdout=subprocess.DEVNULL)


if __name__ == "__main__":
    main()
