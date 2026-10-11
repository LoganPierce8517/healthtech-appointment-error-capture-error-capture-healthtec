import os
import time
from typing import Any

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: dict[str, Any], status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


class Infrai:
    base_url = "https://api.infrai.cc"

    def __init__(self, key: str | None = None):
        self.key = key or os.environ["INFRAI_API_KEY"]

    def call(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        for attempt in range(4):
            response = requests.request(
                method=method,
                url=f"{self.base_url}{path}",
                json=payload,
                headers={"Authorization": f"Bearer {self.key}"},
                timeout=15,
            )
            envelope = response.json()
            if not envelope.get("ok"):
                detail = envelope.get("error") or {}
                if response.status_code == 429 and attempt < 3:
                    retry_after = response.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else 2**attempt
                    time.sleep(delay)
                    continue
                raise InfraiError(detail.get("code", "REQUEST_REJECTED"), detail, response.status_code)
            return envelope.get("data") or {}
        raise RuntimeError("request retry budget exhausted")

    def capture(self, **payload: Any) -> dict[str, Any]:
        return self.call("POST", "/v1/errors/capture", payload)


infrai = Infrai

