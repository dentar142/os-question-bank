# -*- coding: utf-8 -*-
"""题库本地启动器
1) 用 http://127.0.0.1:8765 提供本目录下的页面（避免 file:// 的各种限制）
2) 把 /v1/* 反向代理到本地 LLM 网关 http://127.0.0.1:3425，绕开浏览器跨域

用法：双击，或在本目录执行  python 题库服务.py
"""
import json
import os
import sys
import threading
import urllib.error
import urllib.request
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

UPSTREAM = "http://127.0.0.1:3425"
PORT = 8765
ROOT = os.path.dirname(os.path.abspath(__file__))


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def log_message(self, fmt, *args):
        if os.environ.get("QB_VERBOSE"):
            sys.stdout.write("  %s\n" % (fmt % args))

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def _proxy(self, method):
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else None
        req = urllib.request.Request(UPSTREAM + self.path, data=body, method=method)
        ctype = self.headers.get("Content-Type")
        if ctype:
            req.add_header("Content-Type", ctype)
        auth = self.headers.get("Authorization")
        if auth:
            req.add_header("Authorization", auth)
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data, code = r.read(), r.status
        except urllib.error.HTTPError as e:
            data, code = e.read(), e.code
        except Exception as e:
            data = json.dumps({"error": {"message": "上游不可达: %s" % e}}).encode()
            code = 502
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self._cors()
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path.startswith("/v1/"):
            return self._proxy("POST")
        self.send_error(404)

    def do_GET(self):
        if self.path.startswith("/v1/"):
            return self._proxy("GET")
        return super().do_GET()


def main():
    no_open = "--no-open" in sys.argv or "--silent" in sys.argv
    try:
        srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    except OSError as e:
        sys.stdout.write("端口 %d 已被占用，可能已经在运行（%s）\n" % (PORT, e))
        return
    page = "file:///" + os.path.join(ROOT, "题库.html").replace(os.sep, "/")
    print("题库服务已启动")
    print("  页面: %s" % page)
    print("        （用 file:// 打开，做题进度和以前是同一份；服务只负责代理）")
    print("  代理: http://127.0.0.1:%d/v1/*  ->  %s/v1/*" % (PORT, UPSTREAM))
    print("  Ctrl+C 停止")
    if not no_open:
        threading.Timer(0.8, lambda: webbrowser.open(page)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")


if __name__ == "__main__":
    main()
