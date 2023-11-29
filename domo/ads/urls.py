from ads.views import ManageAds, get_all_active_ads_link, google_cb
from django.urls import path

urlpatterns = [
    path(
        "v1/google-cb",
        google_cb,
        name="ads_google_cb",
    ),
    path(
        "v1/active",
        get_all_active_ads_link,
        name="ads_get_all_active_link",
    ),
]
