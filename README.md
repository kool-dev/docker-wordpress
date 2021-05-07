![CI/CD](https://github.com/kool-dev/docker-wordpress/workflows/CI/CD/badge.svg)

## Description

Minimal PHP Docker image for wordpress based on [kooldev/php](https://github.com/kool-dev/docker-php). It's use is intended for [kool.dev](https://github.com/kool-dev/kool), but can fit in any other PHP use-case.

## Available Tags

### 7.4

- [7.4](https://github.com/kool-dev/docker-wordpress/blob/master/7.4/Dockerfile)
- [7.4-prod](https://github.com/kool-dev/docker-wordpress/blob/master/7.4-prod/Dockerfile)
- [7.4-nginx](https://github.com/kool-dev/docker-wordpress/blob/master/7.4-nginx/Dockerfile)
- [7.4-nginx-prod](https://github.com/kool-dev/docker-wordpress/blob/master/7.4-nginx-prod/Dockerfile)

## How to

Check [kooldev/php](https://github.com/kool-dev/docker-php) to see available options.

### Update images with templates

You should change `fwd-template.json` for configuration and `template` folder for the actual base templates.

After any changes, we need to run `kool run template` to parse the templates and generate all versions folder/files.
