#! /bin/bash

docker build --pull -t kooldev/wordpress:7.4-fpm-alpine 7.4-fpm-alpine
docker build --pull -t kooldev/wordpress:7.3-fpm-alpine 7.3-fpm-alpine
docker build --pull -t kooldev/wordpress:7.2-fpm-alpine 7.2-fpm-alpine
docker build --pull -t kooldev/wordpress:7.1-fpm-alpine 7.1-fpm-alpine
