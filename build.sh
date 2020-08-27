#! /bin/bash

docker build --pull -t kooldev/wordpress:7.1 7.1
docker build -t kooldev/wordpress:7.1-nginx 7.1-nginx
docker build --pull -t kooldev/wordpress:7.2 7.2
docker build -t kooldev/wordpress:7.2-nginx 7.2-nginx
docker build --pull -t kooldev/wordpress:7.3 7.3
docker build -t kooldev/wordpress:7.3-nginx 7.3-nginx
docker build --pull -t kooldev/wordpress:7.4 7.4
docker build -t kooldev/wordpress:7.4-nginx 7.4-nginx
