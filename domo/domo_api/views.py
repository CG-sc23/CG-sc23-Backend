from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as PasswordValidationError
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from pydantic import ValidationError
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.views import APIView


@api_view(["GET"])
def health_check(request):
    return JsonResponse({"status": "ok"})
