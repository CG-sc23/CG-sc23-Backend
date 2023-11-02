from django.http import JsonResponse
from domo_api.http_model import SimpleSuccessResponse
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView


class Deactivate(APIView):
    authentication_classes = [TokenAuthentication]

    def delete(self, request):
        request.user.is_active = False
        request.user.save()

        return JsonResponse(
            SimpleSuccessResponse(success=True).model_dump(),
        )
