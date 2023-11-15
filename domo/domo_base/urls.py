from django.contrib import admin
from django.urls import path
from domo_api.views import auth, external_history, media, project, social_auth, user

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "auth/v1/social/kakao",
        social_auth.Kakao.as_view(),
        name="kakao",
    ),
    path(
        "auth/v1/social/naver",
        social_auth.Naver.as_view(),
        name="naver",
    ),
    path("auth/v1/social/sign-up", auth.SocialSignUp.as_view(), name="social_sign_up"),
    path("auth/v1/sign-up", auth.SignUp.as_view(), name="sign_up"),
    path("auth/v1/sign-in", auth.SignIn.as_view(), name="sign_in"),
    path("auth/v1/sign-out", auth.SignOut.as_view(), name="sign_out"),
    path(
        "auth/v1/password-reset",
        auth.PasswordReset.as_view(),
        name="password_reset",
    ),
    path(
        "auth/v1/password-reset-check",
        auth.PasswordResetCheck.as_view(),
        name="password_reset_check",
    ),
    path(
        "auth/v1/password-reset-confirm",
        auth.PasswordResetConfirm.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "auth/v1/password-change",
        auth.PasswordChange.as_view(),
        name="password_change",
    ),
    path(
        "auth/v1/sign-up-email-verify",
        auth.SignUpEmailVerify.as_view(),
        name="email_verify",
    ),
    path(
        "auth/v1/sign-up-email-verify-confirm",
        auth.SignUpEmailVerifyConfirm.as_view(),
        name="email_verify_confirm",
    ),
    path(
        "external-history/v1/github/check",
        external_history.GithubAccountCheck.as_view(),
        name="github_account_check",
    ),
    path(
        "external-history/v1/github/status",
        external_history.GithubUpdateStatus.as_view(),
        name="get_github_update_status",
    ),
    path(
        "external-history/v1/github/stack",
        external_history.GithubStack.as_view(),
        name="get_github_stack",
    ),
    path(
        "external-history/v1/github/keyword",
        external_history.GithubKeyword.as_view(),
        name="get_github_keyword",
    ),
    path(
        "external-history/v1/github/update",
        external_history.GithubManualUpdate.as_view(),
        name="github_manual_update",
    ),
    path(
        "user/v1",
        user.Info.as_view(),
        name="user_info",
    ),
    path(
        "user/v1/detail/own",
        user.DetailInfo.as_view(),
        name="user_detail_info",
    ),
    path(
        "user/v1/detail/<int:user_id>",
        user.PublicDetailInfo.as_view(),
        name="user_public_detail_info",
    ),
    path(
        "project/v1",
        project.Info.as_view(),
        name="project_info",
    ),
    path(
        "user/v1/projects",
        user.ProjectInfo.as_view(),
        name="user_project_info",
    ),
    path(
        "resource/v1/pre-signed-url/<str:file_name>",
        media.PreSignedUrl.as_view(),
        name="pre_signed_url",
    ),
]
