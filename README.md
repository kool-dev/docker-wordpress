![CI/CD](https://github.com/kool-dev/docker-wordpress/workflows/CI/CD/badge.svg)

## Description

Minimal PHP Docker image for wordpress based on [kooldev/php](https://github.com/kool-dev/docker-php). It's use is intended for [kool.dev](https://github.com/kool-dev/kool), but can fit in any other PHP use-case.

## Available Tags

### 8.4

- [8.4-nginx](https://github.com/kool-dev/docker-wordpress/blob/master/8.4-nginx/Dockerfile)
- [8.4-nginx-prod](https://github.com/kool-dev/docker-wordpress/blob/master/8.4-nginx-prod/Dockerfile)

### 8.3

- [8.3-nginx](https://github.com/kool-dev/docker-wordpress/blob/master/8.3-nginx/Dockerfile)
- [8.3-nginx-prod](https://github.com/kool-dev/docker-wordpress/blob/master/8.3-nginx-prod/Dockerfile)

### 8.2

- [8.2-nginx](https://github.com/kool-dev/docker-wordpress/blob/master/8.2-nginx/Dockerfile)
- [8.2-nginx-prod](https://github.com/kool-dev/docker-wordpress/blob/master/8.2-nginx-prod/Dockerfile)

### 8.1

- [8.1-nginx](https://github.com/kool-dev/docker-wordpress/blob/master/8.1-nginx/Dockerfile)
- [8.1-nginx-prod](https://github.com/kool-dev/docker-wordpress/blob/master/8.1-nginx-prod/Dockerfile)

### Legacy Images

Previously supported but now deprecated tags: [8.3](https://github.com/kool-dev/docker-wordpress/blob/master/8.3/Dockerfile), [8.3-prod](https://github.com/kool-dev/docker-wordpress/blob/master/8.3-prod/Dockerfile), [8.2](https://github.com/kool-dev/docker-wordpress/blob/master/8.2/Dockerfile), [8.2-prod](https://github.com/kool-dev/docker-wordpress/blob/master/8.2-prod/Dockerfile), [8.1](https://github.com/kool-dev/docker-wordpress/blob/master/8.1/Dockerfile), [8.1-prod](https://github.com/kool-dev/docker-wordpress/blob/master/8.1-prod/Dockerfile), [8.0](https://github.com/kool-dev/docker-wordpress/blob/master/8.0/Dockerfile), [8.0-prod](https://github.com/kool-dev/docker-wordpress/blob/master/8.0-prod/Dockerfile), [7.4](https://github.com/kool-dev/docker-wordpress/blob/master/7.4/Dockerfile), [7.4-prod](https://github.com/kool-dev/docker-wordpress/blob/master/7.4-prod/Dockerfile), [7.4-nginx](https://github.com/kool-dev/docker-wordpress/blob/master/7.4-nginx/Dockerfile), [7.4-nginx-prod](https://github.com/kool-dev/docker-wordpress/blob/master/7.4-nginx-prod/Dockerfile), [8.0-nginx](https://github.com/kool-dev/docker-wordpress/blob/master/8.0-nginx/Dockerfile), [8.0-nginx-prod](https://github.com/kool-dev/docker-wordpress/blob/master/8.0-nginx-prod/Dockerfile).

## How to

Check [kooldev/php](https://github.com/kool-dev/docker-php) to see available options.

### Parent image updates

CI rebuilds on `docker-php-updated` repository dispatches after PHP parent
publication, relying on the PHP parent's scheduled rebuild rather than a separate
WordPress schedule. Push, pull request, and manual runs remain available.
Native AMD64 and ARM64 jobs each build once with fresh parent stages and run the
PHP, WP-CLI, NGINX, Supervisor, and WordPress checks on that same local image.
Dispatch delivery does not guarantee a successful downstream build;
check the CI/CD run before treating published tags as refreshed.

Only non-PR runs on this repository's `master` can log in or publish. After all
checks in each native job pass, it pushes the tested image to a staging tag:
`ci-wordpress-<run_id>-<run_attempt>-<variant>-<arch>`. Run/attempt-scoped artifacts
record the staging tag, architecture, and immutable repository digest. PRs, forks,
and manual feature-branch runs only build and test.

After all 16 native jobs succeed, publication validates all eight AMD64/ARM64
pairs and their remote image architectures before changing any stable tag.
Stable manifests reference those exact tested digests; publication never rebuilds.
If a run partially fails, **rerun the entire workflow**, not just failed jobs:
artifacts from earlier attempts are intentionally excluded. Registry updates to
eight tags are not atomic; if promotion fails midway, rerun the entire workflow
to refresh the complete set. Staging tags are not public compatibility tags.

Publication contract tests run with `python3 -m unittest discover -s .github/tests -v`.
For an opt-in real registry test, run `python3 .github/tests/local_registry.py`
with Docker and Buildx available. It creates/removes a loopback-only `registry:2`
container and verifies promotion of 16 synthetic scratch manifests, without
production credentials or WordPress builds.

The existing PHP 8.1 tags are retained, but PHP 8.1 is end-of-life and its Kool
parent is no longer rebuilt by docker-php. Rebuilding WordPress cannot patch an
unmaintained parent; use a maintained PHP tag.

### Update images with templates

You should change `fwd-template.json` for configuration and `template` folder for the actual base templates.

After any changes, we need to run `kool run template` to parse the templates and generate all versions folder/files.
