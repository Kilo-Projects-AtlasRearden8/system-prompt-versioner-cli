import http.client
import json
import urllib.error
import urllib.request


class ClientError(Exception):
    pass


class OpenAIClient:
    def __init__(self, timeout=30):
        self.timeout = timeout

    def chat(self, endpoint, model, system_prompt, user_message):
        url = endpoint.rstrip("/") + "/chat/completions"
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        }
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read()
        except urllib.error.HTTPError as exc:
            raise ClientError(f"endpoint returned HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise ClientError(f"could not reach endpoint {endpoint}: {exc}") from exc
        except http.client.HTTPException as exc:
            raise ClientError(f"endpoint request failed: {exc}") from exc
        try:
            parsed = json.loads(body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ClientError("endpoint returned invalid JSON") from exc
        try:
            return parsed["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ClientError("endpoint returned unexpected response shape") from exc
