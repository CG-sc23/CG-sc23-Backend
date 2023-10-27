from django.contrib import admin
from django.urls import path
from domo_api.views import auth, health_check, social_auth

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", health_check.check, name="health_check"),
    path(
        "api/auth/v1/social/google/sign-in",
        social_auth.Google.sign_in,
        name="google_sign_in",
    ),
    path(
        "api/auth/v1/social/google/callback/",
        social_auth.Google.callback,
        name="google_callback",
    ),
    path(
        "api/auth/v1/social/kakao/sign-in",
        social_auth.Kakao.sign_in,
        name="kakao_sign_in",
    ),
    path(
        "api/auth/v1/social/kakao/callback/",
        social_auth.Kakao.callback,
        name="kakao_callback",
    ),
    path(
        "api/auth/v1/social/sign-up", auth.SocialSignUp.as_view(), name="social_sign_up"
    ),
    path("api/auth/v1/sign-up", auth.SignUp.as_view(), name="sign_up"),
    path("api/auth/v1/sign-in", auth.SignIn.as_view(), name="sign_in"),
    path("api/auth/v1/sign-out", auth.SignOut.as_view(), name="sign_out"),
    path(
        "api/auth/v1/password-reset",
        auth.PasswordReset.as_view(),
        name="password_reset",
    ),
    path(
        "api/auth/v1/password-reset-check",
        auth.PasswordResetCheck.as_view(),
        name="password_reset_check",
    ),
    path(
        "api/auth/v1/password-reset-confirm",
        auth.PasswordResetConfirm.as_view(),
        name="password_reset_confirm",
    ),
]
