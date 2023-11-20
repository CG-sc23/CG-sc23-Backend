from auths.views import auth, social_auth
from django.urls import path

urlpatterns = [
    path(
        "v1/social/kakao",
        social_auth.Kakao.as_view(),
        name="kakao",
    ),
    path(
        "v1/social/naver",
        social_auth.Naver.as_view(),
        name="naver",
    ),
    path("v1/social/sign-up", auth.SocialSignUp.as_view(), name="social_sign_up"),
    path("v1/sign-up", auth.SignUp.as_view(), name="sign_up"),
    path("v1/sign-in", auth.SignIn.as_view(), name="sign_in"),
    path("v1/sign-out", auth.SignOut.as_view(), name="sign_out"),
    path(
        "v1/password-reset",
        auth.PasswordReset.as_view(),
        name="password_reset",
    ),
    path(
        "v1/password-reset-check",
        auth.PasswordResetCheck.as_view(),
        name="password_reset_check",
    ),
    path(
        "v1/password-reset-confirm",
        auth.PasswordResetConfirm.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "v1/password-change",
        auth.PasswordChange.as_view(),
        name="password_change",
    ),
    path(
        "v1/sign-up-email-verify",
        auth.SignUpEmailVerify.as_view(),
        name="email_verify",
    ),
    path(
        "v1/sign-up-email-verify-confirm",
        auth.SignUpEmailVerifyConfirm.as_view(),
        name="email_verify_confirm",
    ),
]
