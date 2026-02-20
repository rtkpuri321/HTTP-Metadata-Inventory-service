from functools import lru_cache

from django.conf import settings

from .background import BackgroundScheduler
from .collector import MetadataCollector
from .repository import MetadataRepository
from .services import MetadataService


@lru_cache(maxsize=1)
def get_metadata_service() -> MetadataService:
    repository = MetadataRepository(
        mongo_uri=settings.MONGO_URI,
        database_name=settings.MONGO_DATABASE,
        collection_name=settings.MONGO_COLLECTION,
        connect_retries=settings.MONGO_CONNECT_RETRIES,
        retry_delay_seconds=settings.MONGO_CONNECT_RETRY_DELAY_SECONDS,
    )
    collector = MetadataCollector(
        timeout_seconds=settings.HTTP_TIMEOUT_SECONDS,
        max_body_bytes=settings.HTTP_MAX_BODY_BYTES,
    )
    return MetadataService(repository=repository, collector=collector)


@lru_cache(maxsize=1)
def get_background_scheduler() -> BackgroundScheduler:
    return BackgroundScheduler(max_workers=settings.BACKGROUND_WORKERS)
