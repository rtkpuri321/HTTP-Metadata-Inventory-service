from collections.abc import Callable
from typing import Optional

import pytest

from metadata_service.collector import CollectedMetadata
from metadata_service.services import MetadataService


class InMemoryRepo:
    def __init__(self) -> None:
        self.data: dict[str, dict] = {}

    def get(self, normalized_url: str) -> Optional[dict]:
        return self.data.get(normalized_url)

    def upsert(self, normalized_url: str, payload: dict) -> dict:
        self.data[normalized_url] = payload
        return payload


class HappyCollector:
    def fetch(self, url: str) -> CollectedMetadata:
        return CollectedMetadata(
            headers={"content-type": "text/html"},
            cookies={"token": "123"},
            page_source=f"<html>{url}</html>",
        )


class FakeScheduler:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def submit_once(self, normalized_url: str, task: Callable[[], None]) -> bool:
        self.calls.append(normalized_url)
        return True


@pytest.fixture
def api_dependencies(monkeypatch):
    from metadata_service import views

    repo = InMemoryRepo()
    service = MetadataService(repository=repo, collector=HappyCollector())
    scheduler = FakeScheduler()

    monkeypatch.setattr(views, "get_metadata_service", lambda: service)
    monkeypatch.setattr(views, "get_background_scheduler", lambda: scheduler)
    return service, scheduler


@pytest.mark.django_db
def test_post_collects_and_stores(api_client, api_dependencies) -> None:
    response = api_client.post("/api/metadata/", {"url": "https://example.com"}, format="json")
    assert response.status_code == 201
    assert response.data["normalized_url"] == "https://example.com/"
    assert response.data["cookies"]["token"] == "123"


@pytest.mark.django_db
def test_get_returns_existing_record(api_client, api_dependencies) -> None:
    service, _ = api_dependencies
    service.collect_and_store("https://example.com")

    response = api_client.get("/api/metadata/?url=https://example.com")
    assert response.status_code == 200
    assert response.data["normalized_url"] == "https://example.com/"


@pytest.mark.django_db
def test_get_miss_returns_202_and_schedules_collection(api_client, api_dependencies) -> None:
    _, scheduler = api_dependencies

    response = api_client.get("/api/metadata/?url=https://cache-miss.example")
    assert response.status_code == 202
    assert scheduler.calls == ["https://cache-miss.example/"]


@pytest.mark.django_db
def test_get_rejects_invalid_url(api_client, api_dependencies) -> None:
    response = api_client.get("/api/metadata/?url=not-a-url")
    assert response.status_code == 400
