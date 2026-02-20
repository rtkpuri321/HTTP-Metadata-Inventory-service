import time
from typing import Any, Optional

from pymongo import ASCENDING, MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from .schemas import MetadataCollectionSchema


class MetadataRepository:
    def __init__(
        self,
        mongo_uri: str,
        database_name: str,
        collection_name: str,
        connect_retries: int,
        retry_delay_seconds: float,
    ) -> None:
        self.mongo_uri = mongo_uri
        self.database_name = database_name
        self.collection_name = collection_name
        self.connect_retries = connect_retries
        self.retry_delay_seconds = retry_delay_seconds
        self._client: Optional[MongoClient] = None
        self._collection: Optional[Collection] = None

    @property
    def collection(self) -> Collection:
        if self._collection is None:
            self._connect()
        assert self._collection is not None
        return self._collection

    def _connect(self) -> None:
        last_error: Optional[Exception] = None
        for _ in range(self.connect_retries):
            try:
                client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=2500)
                client.admin.command("ping")
                collection = client[self.database_name][self.collection_name]
                collection.create_index(
                    [(MetadataCollectionSchema.UNIQUE_KEY, ASCENDING)], unique=True
                )
                self._client = client
                self._collection = collection
                return
            except Exception as exc:  # pragma: no cover - defensive retry branch
                last_error = exc
                time.sleep(self.retry_delay_seconds)

        raise RuntimeError(f"Could not connect to MongoDB after retries: {last_error}")

    def get(self, normalized_url: str) -> Optional[dict[str, Any]]:
        try:
            doc = self.collection.find_one(
                {MetadataCollectionSchema.UNIQUE_KEY: normalized_url}
            )
        except PyMongoError:
            self._collection = None
            doc = self.collection.find_one(
                {MetadataCollectionSchema.UNIQUE_KEY: normalized_url}
            )

        if doc is None:
            return None
        doc.pop(MetadataCollectionSchema.ID, None)
        return doc

    def upsert(self, normalized_url: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            self.collection.update_one(
                {MetadataCollectionSchema.UNIQUE_KEY: normalized_url},
                {"$set": payload},
                upsert=True,
            )
        except PyMongoError:
            self._collection = None
            self.collection.update_one(
                {MetadataCollectionSchema.UNIQUE_KEY: normalized_url},
                {"$set": payload},
                upsert=True,
            )
        return payload
