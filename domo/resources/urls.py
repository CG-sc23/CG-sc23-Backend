from django.urls import path
from resources import views as media

urlpatterns = [
    path(
        "v1/pre-signed-url/<str:file_name>",
        media.PreSignedUrl.as_view(),
        name="pre_signed_url",
    ),
    path(
        "v1/pre-signed-url/profile-image/<str:file_name>",
        media.ProfileImagePreSignedUrl.as_view(),
        name="profile_image_pre_signed_url",
    ),
]
