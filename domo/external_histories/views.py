import csv
import logging
import os
from datetime import datetime, timezone

import requests
from common.const import ReturnCode
from common.http_model import SimpleFailResponse, SimpleSuccessResponse
from common.tasks import update_github_history
from django.http import JsonResponse
from external_histories.http_model import (
    GetAllUserKeywordResponse,
    GetAllUserStackResponse,
    GetCommonStackResponse,
    GetGithubUpdateStatusResponse,
    GithubAccountCheckRequest,
)
from external_histories.models import GithubStatus, UserKeyword, UserStack
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
            response = GetGithubUpdateStatusResponse(
                success=True,
                status=github_status.status,
                last_update=github_status.last_update,
            )
            return JsonResponse(response.model_dump(), status=200)

        except GithubStatus.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Github status Not Found"
                ).model_dump(),
                status=404,
            )


class GithubStack(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            github_status = GithubStatus.objects.get(user=request.user)

        except GithubStatus.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Github status Not Found"
                ).model_dump(),
                status=404,
            )

        if github_status.status == ReturnCode.GITHUB_STATUS_IN_PROGRESS:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Github status is in progress"
                ).model_dump(),
                status=503,
            )

        if github_status.status == ReturnCode.GITHUB_STATUS_FAILED:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Github status failed to update"
                ).model_dump(),
                status=503,
            )

        github_stacks = UserStack.objects.filter(user=request.user)

        stacks = {}

        for stack in github_stacks:
            stacks[stack.language] = stack.code_amount

        response = GetAllUserStackResponse(
            success=True, count=github_stacks.count(), stacks=stacks
        )
        return JsonResponse(response.model_dump(), status=200)


class PublicGithubStack(APIView):
    def get(self, request, user_id):
        try:
            github_status = GithubStatus.objects.get(user=user_id)

        except GithubStatus.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Github status Not Found"
                ).model_dump(),
                status=404,
            )

        if github_status.status == ReturnCode.GITHUB_STATUS_IN_PROGRESS:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Github status is in progress"
                ).model_dump(),
                status=503,
            )

        if github_status.status == ReturnCode.GITHUB_STATUS_FAILED:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Github status failed to update"
                ).model_dump(),
                status=503,
            )

        github_stacks = UserStack.objects.filter(user=user_id)

        stacks = {}

        for stack in github_stacks:
            stacks[stack.language] = stack.code_amount

        response = GetAllUserStackResponse(
            success=True, count=github_stacks.count(), stacks=stacks
        )
        return JsonResponse(response.model_dump(), status=200)


class GithubKeyword(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            github_status = GithubStatus.objects.get(user=request.user)

        except GithubStatus.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Github status Not Found"
                ).model_dump(),
                status=404,
            )

        if github_status.status == ReturnCode.GITHUB_STATUS_IN_PROGRESS:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Github status is in progress"
                ).model_dump(),
                status=503,
            )

        if github_status.status == ReturnCode.GITHUB_STATUS_FAILED:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Github status failed to update"
                ).model_dump(),
                status=503,
            )

        github_keywords = UserKeyword.objects.filter(user=request.user).order_by(
            "-count"
        )

        keywords = {}

        for keyword in github_keywords:
            keywords[keyword.keyword] = keyword.count

        response = GetAllUserKeywordResponse(success=True, keywords=keywords)
        return JsonResponse(response.model_dump(), status=200)


class PublicGithubKeyword(APIView):
    def get(self, request, user_id):
        try:
            github_status = GithubStatus.objects.get(user=user_id)

        except GithubStatus.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Github status Not Found"
                ).model_dump(),
                status=404,
            )

        if github_status.status == ReturnCode.GITHUB_STATUS_IN_PROGRESS:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Github status is in progress"
                ).model_dump(),
                status=503,
            )

        if github_status.status == ReturnCode.GITHUB_STATUS_FAILED:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Github status failed to update"
                ).model_dump(),
                status=503,
            )

        github_keywords = UserKeyword.objects.filter(user=user_id).order_by("-count")

        keywords = {}

        for keyword in github_keywords:
            keywords[keyword.keyword] = keyword.count

        response = GetAllUserKeywordResponse(success=True, keywords=keywords)
        return JsonResponse(response.model_dump(), status=200)


class GithubManualUpdate(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if not user.github_link:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="You don't have github link."
                ).model_dump(),
                status=400,
            )

        github_status = GithubStatus.objects.filter(user=user)

        if github_status.exists():
            if github_status.get().status == ReturnCode.GITHUB_STATUS_IN_PROGRESS:
                return JsonResponse(
                    SimpleFailResponse(
                        success=False, reason="Github status is in progress"
                    ).model_dump(),
                    status=503,
                )
            github_status.update(
                user=user,
                status=ReturnCode.GITHUB_STATUS_IN_PROGRESS,
                last_update=datetime.now(tz=timezone.utc),
            )
        else:
            github_status.create(
                user=user,
                status=ReturnCode.GITHUB_STATUS_IN_PROGRESS,
                last_update=datetime.now(tz=timezone.utc),
            )

        try:
            update_github_history.delay(user.id, user.github_link)
        except Exception as e:
            logging.error(e)
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Error updating github history."
                ).model_dump(),
                status=500,
            )

        return JsonResponse(
            SimpleSuccessResponse(success=True).model_dump(),
            status=202,
        )


class CommonStack(APIView):
    def get(self, request, stack):
        f = open(os.getcwd() + "/external_histories/raw_data/common_stack.csv", "r")
        reader = csv.reader(f)

        data = list(reader)

        for row in data:
            if row[2] == stack:
                response = GetCommonStackResponse(success=True, url=row[1], id=row[0])
                return JsonResponse(response.model_dump(), status=200)

        return JsonResponse(
            SimpleFailResponse(success=False, reason="Can't find stack").model_dump(),
            status=404,
        )
