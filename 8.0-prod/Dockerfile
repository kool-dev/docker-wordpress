FROM wordpress:cli-php8.0 as wordpress-cli
FROM wordpress:php8.0-fpm-alpine as wordpress
FROM kooldev/php:8.0-prod


RUN echo "Building Deps" \
    # build-deps
    && apk add --no-cache --virtual .build-deps $PHPIZE_DEPS \
    && docker-php-ext-install -j$(nproc) mysqli \
    # cleanup
    && apk del .build-deps \
    && rm -rf /var/cache/apk/* /tmp/*

COPY --from=wordpress-cli /usr/local/bin/wp /usr/local/bin/wp
COPY --from=wordpress --chown=kool:kool /usr/src/wordpress /kool/wordpress
COPY --from=wordpress --chown=kool:kool /var/www/html/wp-content /app/wp-content
COPY entrypoint /kool/wordpress-entrypoint

RUN chmod -R 777 wp-content && chmod +x /kool/wordpress-entrypoint

ENTRYPOINT [ "/kool/wordpress-entrypoint" ]
CMD [ "supervisord", "-c", "/kool/supervisor.conf" ]
