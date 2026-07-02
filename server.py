#!/usr/bin/env python3
"""Static file server that logs the real client IP from reverse-proxy headers."""

import json
import re
from http.server import HTTPServer, SimpleHTTPRequestHandler


def client_ip(headers, peer: str) -> str:
    if forwarded := headers.get("X-Forwarded-For"):
        return forwarded.split(",")[0].strip()
    if real_ip := headers.get("X-Real-IP"):
        return real_ip.strip()
    if fwd := headers.get("Forwarded"):
        for part in fwd.split(","):
            match = re.search(r'for=(?:"?\[?([^;\],"]+)', part, re.I)
            if match:
                ip = match.group(1).strip('"[]')
                if ip.lower() != "unknown":
                    return ip
    return peer


class Handler(SimpleHTTPRequestHandler):
    def address_string(self) -> str:
        return client_ip(self.headers, self.client_address[0])

    def do_GET(self) -> None:
        if self.path.rstrip("/") == "/__tw/whoami":
            body = json.dumps(
                {
                    "client_ip": client_ip(self.headers, self.client_address[0]),
                    "peer": self.client_address[0],
                    "x_forwarded_for": self.headers.get("X-Forwarded-For"),
                    "x_real_ip": self.headers.get("X-Real-IP"),
                    "forwarded": self.headers.get("Forwarded"),
                },
                indent=2,
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
