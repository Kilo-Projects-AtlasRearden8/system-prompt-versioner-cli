import pytest
from promptv.client import OpenAIClient, ClientError


def test_client_chat_returns_mock_response(mock_endpoint):
    client = OpenAIClient()
    response = client.chat(mock_endpoint, "test-model", "system prompt content", "user message")
    assert "mock response to: system prompt content" in response


def test_client_chat_error_on_bad_endpoint():
    client = OpenAIClient(timeout=1)
    with pytest.raises(ClientError):
        client.chat("http://127.0.0.1:1/", "model", "system", "user")


def test_client_chat_error_on_non_json(mock_endpoint):
    class BadHandler:
        pass
    client = OpenAIClient()
    with pytest.raises(ClientError):
        client.chat("http://127.0.0.1:9999/v1", "model", "system", "user")


def test_client_response_shape_error(mock_endpoint):
    import json
    from http.server import BaseHTTPRequestHandler, HTTPServer
    import threading
    import time

    class ShapeHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            if self.path != "/v1/chat/completions":
                self.send_error(404)
                return
            reply = json.dumps({"unexpected": "shape"}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(reply)

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), ShapeHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.05)
    try:
        client = OpenAIClient()
        with pytest.raises(ClientError):
            client.chat(f"http://127.0.0.1:{port}/v1", "model", "system", "user")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=1)