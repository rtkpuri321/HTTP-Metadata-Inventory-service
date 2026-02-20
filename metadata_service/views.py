import logging

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .dependencies import get_background_scheduler, get_metadata_service
from .exceptions import CollectionError, InvalidURL
from .services import normalize_url, validate_url


logger = logging.getLogger(__name__)


class MetadataView(APIView):
    def post(self, request: Request) -> Response:
        url = request.data.get("url")
        if not isinstance(url, str):
            return Response(
                {"detail": "Field 'url' is required and must be a string."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = get_metadata_service()
        try:
            stored = service.collect_and_store(url)
        except InvalidURL as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except CollectionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        return Response(stored, status=status.HTTP_201_CREATED)

    def get(self, request: Request) -> Response:
        url = request.query_params.get("url")
        if not isinstance(url, str):
            return Response(
                {"detail": "Query parameter 'url' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validated = validate_url(url)
        except InvalidURL as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        service = get_metadata_service()
        existing = service.get(validated)
        if existing:
            return Response(existing, status=status.HTTP_200_OK)

        normalized = normalize_url(validated)
        scheduler = get_background_scheduler()

        scheduled = scheduler.submit_once(
            normalized, lambda: _safe_collect(service=service, url=validated)
        )
        message = (
            "Metadata not found. Background collection started."
            if scheduled
            else "Metadata not found. Background collection already running."
        )
        return Response(
            {"detail": message, "url": validated},
            status=status.HTTP_202_ACCEPTED,
        )


def _safe_collect(*, service, url: str) -> None:
    try:
        service.collect_and_store(url)
    except Exception as exc:  # pragma: no cover - defensive logging path
        logger.exception("Background metadata collection failed for %s: %s", url, exc)
