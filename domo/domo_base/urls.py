"""
URL configuration for domo_base project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from domo_api.views import auth, health_check

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", health_check.check, name="health_check"),
    path("api/auth/v1/sign-up", auth.SignUp, name="sign_up"),
    path("api/auth/v1/sign-in", auth.SignIn, name="sign_in"),
    path("api/auth/v1/sign-out", auth.SignOut, name="sign_out"),
]
