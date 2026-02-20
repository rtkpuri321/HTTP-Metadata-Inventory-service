from django.urls import path

from .views import MetadataView


urlpatterns = [
    path("metadata/", MetadataView.as_view(), name="metadata"),
]
