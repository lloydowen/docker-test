#!/usr/bin/env python3
"""Static file server that logs the real client IP from reverse-proxy headers."""

from http.server import HTTPServer, SimpleHTTPRequestHandler


class Handler(SimpleHTTPRequestHandler):
    def address_string(self) -> str:
        forwarded = self.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if real_ip := self.headers.get("X-Real-IP"):
            return real_ip.strip()
        return self.client_address[0]


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
