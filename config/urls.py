from django.urls import include, path


urlpatterns = [
    path("api/", include("metadata_service.urls")),
]
