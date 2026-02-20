from typing import Optional
from urllib.parse import urlparse, urlunparse

from .collector import MetadataCollector
from .exceptions import InvalidURL
from .repository import MetadataRepository
from .schemas import MetadataDocument, URLRequest


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path or "/"
    normalized = parsed._replace(
        scheme=parsed.scheme.lower(),
        netloc=parsed.netloc.lower(),
        path=path.rstrip("/") or "/",
        params="",
        fragment="",
    )
    return urlunparse(normalized)


def validate_url(url: str) -> str:
    try:
        parsed = URLRequest(url=url)
    except Exception as exc:
        raise InvalidURL(str(exc)) from exc
    return str(parsed.url)


class MetadataService:
    def __init__(self, repository: MetadataRepository, collector: MetadataCollector) -> None:
        self.repository = repository
        self.collector = collector

    def get(self, url: str) -> Optional[dict]:
        normalized = normalize_url(url)
        return self.repository.get(normalized)

    def collect_and_store(self, url: str) -> dict:
        validated_url = validate_url(url)
        normalized = normalize_url(validated_url)
        collected = self.collector.fetch(validated_url)
        record = MetadataDocument.from_payload(
            url=validated_url,
            normalized_url=normalized,
            headers=collected.headers,
            cookies=collected.cookies,
            page_source=collected.page_source,
        )
        return self.repository.upsert(normalized, record.to_mongo())
