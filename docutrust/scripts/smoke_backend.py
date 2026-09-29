import os
import time
from uuid import uuid4

import httpx


BASE_URL = os.getenv("DOCUTRUST_API_URL", "http://localhost:8000")


def main() -> None:
    email = f"smoke-{uuid4().hex[:8]}@example.com"
    password = "DocuTrust123!"

    with httpx.Client(base_url=BASE_URL, timeout=30) as client:
        health = client.get("/health")
        health.raise_for_status()
        print("health:", health.json())

        register = client.post(
            "/register",
            json={"name": "Smoke Test", "email": email, "password": password},
        )
        register.raise_for_status()
        token = register.json()["access_token"]
        print("register: ok")

        profile = client.get("/profile", headers={"Authorization": f"Bearer {token}"})
        profile.raise_for_status()
        print("profile:", profile.json()["email"])

        chat = client.post(
            "/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"question": f"What evidence exists for smoke test {time.time()}?", "top_k": 3},
        )
        chat.raise_for_status()
        print("chat:", chat.json()["retrieval_score"])


if __name__ == "__main__":
    main()
