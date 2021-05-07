#! /bin/bash

docker build --pull -t kooldev/wordpress:7.4 7.4
docker build -t kooldev/wordpress:7.4-prod 7.4-prod
docker build -t kooldev/wordpress:7.4-nginx 7.4-nginx
docker build -t kooldev/wordpress:7.4-nginx-prod 7.4-nginx-prod
