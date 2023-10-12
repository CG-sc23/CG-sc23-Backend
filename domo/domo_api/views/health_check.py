from django.http import JsonResponse
from rest_framework.decorators import api_view


@api_view(["GET"])
def check(request):
    return JsonResponse({"status": "ok"})
