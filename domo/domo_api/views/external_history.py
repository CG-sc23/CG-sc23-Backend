import requests
from django.http import JsonResponse
from domo_api.http_model import (
    GetGithubUpdateStatus,
    GithubAccountCheckRequest,
    SimpleFailResponse,
    SimpleSuccessResponse,
)
from domo_api.models import GithubStatus
from pydantic import ValidationError
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


class GithubAccountCheck(APIView):
    def get(self, request):
        github_link = request.GET.get("github_link")

        # validate input
        try:
            request_data = GithubAccountCheckRequest(github_link=github_link)
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        if "github.com" not in request_data.github_link:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        account = (
            request_data.github_link.split("/")[-1]
            if not request_data.github_link.split("/")[-1] == ""
            else request_data.github_link.split("/")[-2]
        )

        # invalid user input
        if account == "github.com":
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        try:
            check_url = "https://api.github.com/users/" + account
            response = requests.get(url=check_url)
        except:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Github API server doesn't response"
                ).model_dump(),
                # Service Temporarily Unavailable
                status=503,
            )

        if response.status_code != 200:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Can't find github account."
                ).model_dump(),
                status=404,
            )

        return JsonResponse(
            SimpleSuccessResponse(success=True).model_dump(),
            status=200,
        )

    class GithubUpdateStatus(APIView):
        authentication_classes = [TokenAuthentication]
        permission_classes = [IsAuthenticated]

        def get(self, request):
            try:
                github_status = GithubStatus.objects.get(user=request.user)
                response = GetGithubUpdateStatus(
                    status=github_status.status, last_update=github_status.last_update
                )
                return JsonResponse(response.model_dump(), status=200)

            except GithubStatus.DoesNotExist:
                return JsonResponse(
                    SimpleFailResponse(
                        success=False, reason="Github status Not Found "
                    ).model_dump(),
                    status=404,
                )
