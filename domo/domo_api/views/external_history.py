import requests
from django.http import JsonResponse
from domo_api.http_model import (
    GithubAccountCheckRequest,
    SimpleFailResponse,
    SimpleSuccessResponse,
)
from pydantic import ValidationError
from rest_framework.views import APIView


class GithubAccountCheck(APIView):
    def post(self, request):
        account = request.data.get("account")

        data_dict = {
            "account": account,
        }

        # validate input
        try:
            request_data = GithubAccountCheckRequest(**data_dict)
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        try:
            check_url = "https://api.github.com/users/" + request_data.account
            response = requests.get(url=check_url)
        except:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        if response.status_code == 200:
            return JsonResponse(
                SimpleSuccessResponse(success=True).model_dump(),
                status=201,
            )
        else:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Can't find github account."
                ).model_dump(),
                status=401,
            )
