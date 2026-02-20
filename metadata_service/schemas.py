from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, HttpUrl, field_validator

METADATA_COLLECTION = "metadata"


class MetadataCollectionSchema:
    UNIQUE_KEY = "normalized_url"
    ID = "_id"


class URLRequest(BaseModel):
    url: HttpUrl

    @field_validator("url")
    @classmethod
    def enforce_http_scheme(cls, value: HttpUrl) -> HttpUrl:
        if value.scheme not in {"http", "https"}:
            raise ValueError("Only http and https schemes are supported.")
        return value


class MetadataDocument(BaseModel):
    url: str
    normalized_url: str
    headers: dict[str, str]
    cookies: dict[str, str]
    page_source: str
    fetched_at: datetime

    @classmethod
    def from_payload(
        cls,
        *,
        url: str,
        normalized_url: str,
        headers: dict[str, str],
        cookies: dict[str, str],
        page_source: str,
    ) -> "MetadataDocument":
        return cls(
            url=url,
            normalized_url=normalized_url,
            headers=headers,
            cookies=cookies,
            page_source=page_source,
            fetched_at=datetime.now(timezone.utc),
        )

    def to_mongo(self) -> dict[str, Any]:
        return self.model_dump()
