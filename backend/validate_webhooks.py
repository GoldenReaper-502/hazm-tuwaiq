"""Validate webhook dispatch by setting a fake webhook and creating an alert."""
from __future__ import annotations

import importlib.util
import pathlib
import time
import http.server
import threading
import json

spec = importlib.util.spec_from_file_location("backend_cctv", str(pathlib.Path(__file__).resolve().parent / "cctv.py"))
backend_cctv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backend_cctv)


class _ReqHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('content-length', 0))
        body = self.rfile.read(length)
        print('Webhook received:', body.decode())
        self.send_response(200)
        self.end_headers()


def run():
    # start simple HTTP server
    srv = http.server.HTTPServer(('localhost', 9001), _ReqHandler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()

    mgr = backend_cctv.get_manager()
    cam_id = f"web_test_{int(time.time())}"
    cam = backend_cctv.Camera(id=cam_id, name='webcam', rtsp_url='', enabled=False, fps=1.0)
    mgr.create_camera(cam)
    # set webhook rule
    mgr.update_camera_rules(cam_id, {'webhook_url': 'http://localhost:9001/hook'})

    # create an alert
    backend_cctv.store_alert(cam_id, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), 'test_event', 'low', {'foo':'bar'})

    time.sleep(1)
    srv.shutdown()
    print('Webhook test complete')


if __name__ == '__main__':
    run()
