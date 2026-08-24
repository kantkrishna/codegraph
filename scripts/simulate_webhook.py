import hashlib
import hmac
import json

import httpx

SECRET = "super-secret-hmac-key"
URL = "http://localhost:8000/api/v1/webhooks/github"
payload = {
    "ref": "main",
    "repository": {
        "id": 999888,
        "clone_url": "https://github.com/kantkrishna/microservices-demo.git",
    },
}
payload_bytes = json.dumps(payload).encode("utf-8")
signature = "sha256=" + hmac.new(SECRET.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
headers = {
    "X-Hub-Signature-256": signature,
    "X-GitHub-Event": "push",
    "Content-Type": "application/json",
}
response = httpx.post(URL, content=payload_bytes, headers=headers, timeout=15.0)
print(f"Response: {response.status_code} - {response.text}")
