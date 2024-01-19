FROM wordpress:cli-php8.3 as wordpress-cli
FROM wordpress:php8.3-fpm-alpine as wordpress
FROM kooldev/php:8.3-nginx-prod

ENV NGINX_ROOT=/app

COPY --from=wordpress-cli /usr/local/bin/wp /usr/local/bin/wp
COPY --from=wordpress --chown=kool:kool /usr/src/wordpress /kool/wordpress
COPY --from=wordpress --chown=kool:kool /var/www/html/wp-content /app/wp-content
COPY entrypoint /kool/wordpress-entrypoint

RUN chmod -R 777 wp-content && chmod +x /kool/wordpress-entrypoint

ENTRYPOINT [ "/kool/wordpress-entrypoint" ]
CMD [ "supervisord", "-c", "/kool/supervisor.conf" ]
