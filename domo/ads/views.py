import logging
import os
from datetime import datetime, timezone

from ads.http_model import CreateAdRequest
from ads.models import Ads
from common.auth import IsStaff
from common.http_model import SimpleFailResponse, SimpleSuccessResponse
from django.http import JsonResponse
from pydantic import ValidationError
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


@api_view(["POST"])
def google_cb(request):
    try:
        if (
            request.headers["User-Agent"]
            != "Mozilla/5.0 (compatible; Google-Apps-Script; beanserver; +https://script.google.com; id: "
            f"{os.getenv('GOOGLE_SCRIPT_ID')}"
        ):
            raise PermissionError("WHO_ARE_YOU")
    except:
        raise PermissionError("WHO_ARE_YOU")

    responds = request.data.get("results")

    requester_email = request.data.get("requesterEmail")
    requester_name = None
    company_email = None
    company_name = None
    ads_purpose = None
    ads_file_link = None

    for respond in responds:
        if respond["title"] == "회사의 이메일을 입력해주세요.":
            company_email = respond["response"]
        elif respond["title"] == "회사의 이름을 입력해주세요.":
            company_name = respond["response"]
        elif respond["title"] == "담당자의 성함을 입력해주세요.":
            requester_name = respond["response"]
        elif respond["title"] == "광고의 목적은 무엇인가요?":
            ads_purpose = respond["response"]
        elif respond["title"] == "광고로 게시할 사진을 올려주세요. (가로:세로 = 2:1)":
            ads_file_link = respond["response"]

    try:
        request_data = CreateAdRequest(
            requester_email=requester_email,
            requester_name=requester_name,
            company_email=company_email,
            company_name=company_name,
            ads_purpose=ads_purpose,
            ads_file_link=ads_file_link,
        )
    except ValidationError as e:
        logging.error(e)
        return JsonResponse(
            SimpleFailResponse(
                success=False,
                reason="Invalid request.",
            ).model_dump(),
            status=400,
        )

    try:
        Ads.objects.create(
            requester_email=request_data.requester_email,
            requester_name=request_data.requester_name,
            company_email=request_data.company_email,
            company_name=request_data.company_name,
            ads_purpose=request_data.ads_purpose,
            ads_file_link=request_data.ads_file_link,
            created_at=datetime.now(tz=timezone.utc),
        )
    except Exception as e:
        logging.error(e)
        return JsonResponse(
            SimpleFailResponse(
                success=False, reason="Error creating ads request."
            ).model_dump(),
            status=500,
        )

    return JsonResponse(
        SimpleSuccessResponse(
            success=True,
        ).model_dump(),
        status=200,
    )


class ManageAds(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsStaff]

    def get(self, request):
        try:
            ads_requests = Ads.objects.all()
        except Exception as e:
            logging.error(e)
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Error getting ads requests."
                ).model_dump(),
                status=500,
            )

        return JsonResponse(
            SimpleSuccessResponse(
                success=True,
                requests=[
                    {
                        "id": ads_request.id,
                        "requester_email": ads_request.requester_email,
                        "requester_name": ads_request.requester_name,
                        "company_email": ads_request.company_email,
                        "company_name": ads_request.company_name,
                        "ads_purpose": ads_request.ads_purpose,
                        "ads_file_link": ads_request.ads_file_link,
                    }
                    for ads_request in ads_requests
                ],
            ).model_dump(),
            status=200,
        )

    def put(self, request):
        raise NotImplementedError
