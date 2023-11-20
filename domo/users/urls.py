from django.urls import path
from users import views as user

urlpatterns = [
    path(
        "v1",
        user.Info.as_view(),
        name="user_info",
    ),
    path(
        "v1/detail/own",
        user.DetailInfo.as_view(),
        name="user_detail_info",
    ),
    path(
        "v1/detail/<int:user_id>",
        user.PublicDetailInfo.as_view(),
        name="user_public_detail_info",
    ),
    path(
        "v1/inviter",
        user.Inviter.as_view(),
        name="user_inviter",
    ),
    path(
        "v1/invitee",
        user.Invitee.as_view(),
        name="user_inviter",
    ),
    path(
        "v1/invitee/reply",
        user.Invitee.as_view(),
        name="user_inviter_reply",
    ),
]
