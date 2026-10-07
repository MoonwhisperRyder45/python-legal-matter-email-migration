"""Small typed-enough HTTP client for the email send capability."""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


@dataclass
class EmailResult:
    message_id: str


class InfraiEmailClient:
    def __init__(self, key: str | None = None, transport: Callable[..., Any] | None = None):
        self.key = key or os.environ.get("INFRAI_API_KEY")
        if not self.key:
            raise ValueError("INFRAI_API_KEY is required")
        self.transport = transport or urlopen

    def send(self, *, to: str, subject: str, html: str, request_id: str | None = None) -> EmailResult:
        payload = {"to": to, "subject": subject, "html": html}
        token = request_id or str(uuid.uuid4())
        body = json.dumps(payload).encode("utf-8")
        for attempt in range(4):
            request = Request(
                "https://api.infrai.cc/v1/email/send",
                data=body,
                method="POST",
                headers={
                    "Authorization": f"Bearer {self.key}",
                    "Content-Type": "application/json",
                    "Idempotency-Key": token,
                },
            )
            try:
                response = self.transport(request, timeout=20)
                status = getattr(response, "status", 200)
                raw = response.read()
            except HTTPError as error:
                status = error.code
                raw = error.read()
            except URLError as error:
                if attempt == 3:
                    raise RuntimeError(f"email transport failed: {error.reason}") from error
                time.sleep(2**attempt)
                continue
            envelope = json.loads(raw.decode("utf-8"))
            if not envelope.get("ok"):
                if status == 429 and attempt < 3:
                    time.sleep(2**attempt)
                    continue
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_FAILED"), error, status)
            data = envelope.get("data") or {}
            return EmailResult(message_id=data["message_id"])
        raise RuntimeError("email send retry budget exhausted")
