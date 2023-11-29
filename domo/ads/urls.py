from ads.views import ManageAds, google_cb
from django.urls import path

urlpatterns = [
    path(
        "v1/google-cb",
        google_cb,
        name="ads_google_cb",
    ),
    path(
        "v1",
        ManageAds.as_view(),
        name="ads_manage",
    ),
]
