FROM wordpress:php{{ $version }}-fpm-alpine as wordpress
FROM {{ $from }}

@if ($nginx)
ENV NGINX_ROOT=/app
@endif

RUN echo "Building Deps" \
    # build-deps
    && apk add --no-cache --virtual .build-deps $PHPIZE_DEPS \
    && docker-php-ext-install -j$(nproc) mysqli \
    # cleanup
    && apk del .build-deps \
    && rm -rf /var/cache/apk/* /tmp/*

COPY --from=wordpress --chown=kool:kool /usr/src/wordpress /kool/wordpress
COPY --from=wordpress --chown=kool:kool /var/www/html/wp-content /app/wp-content
COPY entrypoint /kool/entrypoint

RUN chmod -R 777 wp-content && chmod +x /kool/entrypoint
