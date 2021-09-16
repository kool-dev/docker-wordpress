FROM wordpress:cli-php{{ $version }} as wordpress-cli
FROM wordpress:php{{ $version }}-fpm-alpine as wordpress
FROM {{ $from }}

@if ($nginx)
ENV NGINX_ROOT=/app
@endif

COPY --from=wordpress-cli /usr/local/bin/wp /usr/local/bin/wp
COPY --from=wordpress --chown=kool:kool /usr/src/wordpress /kool/wordpress
COPY --from=wordpress --chown=kool:kool /var/www/html/wp-content /app/wp-content
COPY entrypoint /kool/wordpress-entrypoint

RUN chmod -R 777 wp-content && chmod +x /kool/wordpress-entrypoint

ENTRYPOINT [ "/kool/wordpress-entrypoint" ]
CMD [ "supervisord", "-c", "/kool/supervisor.conf" ]
