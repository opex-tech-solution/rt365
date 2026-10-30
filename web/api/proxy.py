# Vercel Python function: forwards the browser's requests to Render and adds the secret key.
import os, re, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def _go(self, path, body=None):
        req = urllib.request.Request(os.environ["RENDER_URL"].rstrip("/") + path, data=body,
              headers={"x-api-key": os.environ["RENDER_API_KEY"], "content-type": "application/json"},
              method="POST" if body is not None else "GET")
        try:
            r = urllib.request.urlopen(req, timeout=55)
            code, data, ct = r.status, r.read(), r.headers.get("content-type", "application/json")
        except urllib.error.HTTPError as e:
            code, data, ct = e.code, e.read(), "application/json"
        self.send_response(code); self.send_header("content-type", ct); self.end_headers(); self.wfile.write(data)

    def do_GET(self):
        q = parse_qs(urlparse(self.path).query); op = q.get("op", [""])[0]
        if op == "fields": return self._go("/fields")
        if op == "pdf" and re.fullmatch(r"[\w-]+", q.get("id", [""])[0]): return self._go("/pdf/" + q["id"][0])
        self.send_error(404)

    def do_POST(self):
        self._go("/generate", self.rfile.read(int(self.headers.get("content-length", 0))))
