from django.contrib import admin
from django.urls import path
from domo_api.views import auth, health_check

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", health_check.check, name="health_check"),
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
]
