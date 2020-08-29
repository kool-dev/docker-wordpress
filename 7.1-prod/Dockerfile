FROM wordpress:php7.1-fpm-alpine as wordpress
FROM kooldev/php:7.1-prod


COPY --from=wordpress --chown=kool:kool /usr/src/wordpress /kool/wordpress
COPY --from=wordpress --chown=kool:kool /var/www/html/wp-content /app/wp-content
COPY entrypoint /kool/entrypoint

RUN chmod -R 777 wp-content && chmod +x /kool/entrypoint
