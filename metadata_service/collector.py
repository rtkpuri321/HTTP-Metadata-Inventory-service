from dataclasses import dataclass

import httpx

from .exceptions import CollectionError


@dataclass
class CollectedMetadata:
    headers: dict[str, str]
    cookies: dict[str, str]
    page_source: str


class MetadataCollector:
    def __init__(self, timeout_seconds: float, max_body_bytes: int) -> None:
        self.timeout_seconds = timeout_seconds
        self.max_body_bytes = max_body_bytes

    def fetch(self, url: str) -> CollectedMetadata:
        try:
            with httpx.Client(
                timeout=self.timeout_seconds, follow_redirects=True
            ) as client:
                response = client.get(url)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise CollectionError(f"Failed collecting metadata from '{url}': {exc}") from exc

        body = response.text
        if len(body.encode("utf-8")) > self.max_body_bytes:
            body = body[: self.max_body_bytes]

        return CollectedMetadata(
            headers={k: v for k, v in response.headers.items()},
            cookies={k: v for k, v in response.cookies.items()},
            page_source=body,
        )
