from ads.views import get_active_ad_link, google_cb
from django.urls import path

urlpatterns = [
    path(
        "v1/google-cb",
        google_cb,
        name="ads_google_cb",
    ),
    path(
        "v1/active",
        get_active_ad_link,
        name="ads_get_all_active_link",
    ),
]
