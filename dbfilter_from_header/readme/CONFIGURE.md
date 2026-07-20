Please keep in mind that the standard odoo dbfilter configuration is
still applied before looking at the regular expression in the header.

- For nginx, use:

  `proxy_set_header X-Odoo-dbfilter [your filter regex];`

- For caddy, use:

  `proxy_header X-Odoo-dbfilter [your filter regex]`

- For Apache, use:

  `RequestHeader set X-Odoo-dbfilter [your filter regex]`

And make sure that proxy mode is enabled in Odoo's configuration file:

`proxy_mode = True`

Note that Odoo 19 also ships its own `X-Odoo-Database` header, which selects
one exact database rather than filtering with a regular expression, and makes
the session stateless. The two are not interchangeable, and Odoo refuses a
request that carries both an `X-Odoo-Database` header and a `session_id`
cookie. Keep sending `X-Odoo-dbfilter` and do not mix the two headers.
