# WordPress WebP support: automatically serve WebP images when available and supported
location ~* ^(.+)\.(jpe?g|png)$ {
    set $webp_suffix "";
    
    # Check if WebP is supported by the client
    if ($http_accept ~* "image/webp") {
        set $webp_suffix ".webp";
    }
    
    # Try to serve the WebP version first, then fallback to original
    try_files $uri$webp_suffix $uri /index.php?$query_string;
    
    # Set appropriate cache headers for images
    expires 30d;
    add_header Cache-Control "public, immutable";
    add_header Vary "Accept";
}