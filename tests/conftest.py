import json
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest


class MockHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/v1/chat/completions":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self.send_error(400)
            return
        system = ""
        for message in payload.get("messages", []):
            if message.get("role") == "system":
                system = message.get("content", "")
                break
        content = f"mock response to: {system[:80]}"
        reply = {
            "id": "mock",
            "object": "chat.completion",
            "created": 0,
            "model": payload.get("model", "mock"),
            "choices": [
                {"index": 0, "message": {"role": "assistant", "content": content}, "finish_reason": "stop"}
            ],
        }
        reply_bytes = json.dumps(reply).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(reply_bytes)))
        self.end_headers()
        self.wfile.write(reply_bytes)

    def log_message(self, *args):
        pass


@pytest.fixture(scope="session")
def mock_endpoint():
    server = HTTPServer(("127.0.0.1", 0), MockHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.05)
    yield f"http://127.0.0.1:{port}/v1"
    server.shutdown()
    server.server_close()
    thread.join(timeout=1)


@pytest.fixture
def temp_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("PROMPTV_CONFIG_DIR", str(tmp_path / "config"))
    monkeypatch.setenv("PROMPTV_DATA_DIR", str(tmp_path / "data"))
    yield tmp_path


@pytest.fixture
def run_cli(monkeypatch):
    def _run(argv, capture=True):
        from promptv.cli import main
        import io
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        try:
            if capture:
                sys.stdout = stdout_capture
                sys.stderr = stderr_capture
            try:
                return main(argv), stdout_capture.getvalue(), stderr_capture.getvalue()
            except SystemExit as exc:
                return exc.code, stdout_capture.getvalue(), stderr_capture.getvalue()
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    return _run