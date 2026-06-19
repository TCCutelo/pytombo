"""Tiny webhook server that auto-deploys on push to main (stdlib only)."""

import hashlib
import hmac
import json
import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

SECRET = os.environ["WEBHOOK_SECRET"].encode()
PORT = int(os.environ.get("WEBHOOK_PORT", "9011"))
DEPLOY_CMD = (
    "cd /opt/pytombo "
    "&& sudo -u pytombo -H git pull --ff-only "
    "&& sudo -u pytombo -H /usr/local/bin/uv sync "
    "&& systemctl restart pytombo"
)


def verify_signature(payload, signature):
    expected = "sha256=" + hmac.new(SECRET, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/deploy":
            return self._reply(404, b"not found")

        length = int(self.headers.get("Content-Length", 0))
        payload = self.rfile.read(length)
        signature = self.headers.get("X-Hub-Signature-256", "")
        if not verify_signature(payload, signature):
            return self._reply(403, b"bad signature")

        if self.headers.get("X-GitHub-Event") != "push":
            return self._reply(200, b"ignored")

        data = json.loads(payload or b"{}")
        if data.get("ref") != "refs/heads/main":
            return self._reply(200, b"not main")

        subprocess.Popen(["bash", "-c", DEPLOY_CMD])
        return self._reply(200, b"deploying")

    def _reply(self, code, body):
        self.send_response(code)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
