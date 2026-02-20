from typing import Optional

from metadata_service.collector import CollectedMetadata
from metadata_service.services import MetadataService, normalize_url, validate_url


class DummyRepository:
    def __init__(self) -> None:
        self.store: dict[str, dict] = {}

    def get(self, normalized_url: str) -> Optional[dict]:
        return self.store.get(normalized_url)

    def upsert(self, normalized_url: str, payload: dict) -> dict:
        self.store[normalized_url] = payload
        return payload


class DummyCollector:
    def fetch(self, url: str) -> CollectedMetadata:
        return CollectedMetadata(
            headers={"server": "dummy"},
            cookies={"sessionid": "abc"},
            page_source=f"<html>{url}</html>",
        )


def test_normalize_url_trims_case_and_fragment() -> None:
    normalized = normalize_url("HTTPS://Example.com/path/?a=1#section")
    assert normalized == "https://example.com/path?a=1"


def test_validate_url_rejects_non_http_scheme() -> None:
    try:
        validate_url("ftp://example.com")
        assert False, "Expected validation to fail"
    except Exception:
        assert True


def test_collect_and_store_persists_payload() -> None:
    repo = DummyRepository()
    service = MetadataService(repository=repo, collector=DummyCollector())
    result = service.collect_and_store("https://example.com")

    assert result["normalized_url"] == "https://example.com/"
    assert result["headers"]["server"] == "dummy"
    assert "fetched_at" in result
