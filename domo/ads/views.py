import logging
import os
from datetime import datetime, timezone

from ads.http_model import CreateAdRequest, GetAdLinkResponse
from ads.models import Ad
from common.http_model import SimpleFailResponse, SimpleSuccessResponse
from django.db.transaction import atomic
from django.http import JsonResponse
from pydantic import ValidationError
from rest_framework.decorators import api_view


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
            ads_file_link = f"https://drive.google.com/open?id={respond['response'][0]}"

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
        Ad.objects.create(
            requester_email=request_data.requester_email,
            requester_name=request_data.requester_name,
            company_email=request_data.company_email,
            company_name=request_data.company_name,
            purpose=request_data.ads_purpose,
            file_link=request_data.ads_file_link,
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


@atomic
@api_view(["GET"])
def get_active_ad_link(request):
    try:
        ads_count = Ad.objects.filter(
            is_active=True,
            initial_exposure_count__isnull=False,
            remaining_exposure_count__isnull=False,
        ).count()
        if ads_count == 0:
            return JsonResponse(
                GetAdLinkResponse(success=True, file_link="").model_dump(),
                status=200,
            )

        idx_obj = Ad.objects.get(
            is_active=False,
            requester_email="RR",
            requester_name="RR",
            company_email="RR",
            company_name="RR",
            purpose="RR",
        )

        # inital_exposure_count를 idx로 사용
        curr_idx = idx_obj.initial_exposure_count

        idx_obj.initial_exposure_count = (curr_idx + 1) % ads_count
        idx_obj.save()

        ads = Ad.objects.filter(
            is_active=True, remaining_exposure_count__gt=0
        ).order_by("-remaining_exposure_count", "created_at")

        will_be_exposed_ad = ads[curr_idx]
        will_be_exposed_ad.remaining_exposure_count -= 1
        if will_be_exposed_ad.remaining_exposure_count == 0:
            will_be_exposed_ad.is_active = False
        will_be_exposed_ad.save()

    except IndexError:
        curr_idx = 0
        will_be_exposed_ad = ads[curr_idx]
        will_be_exposed_ad.remaining_exposure_count -= 1
        if will_be_exposed_ad.remaining_exposure_count == 0:
            will_be_exposed_ad.is_active = False
        will_be_exposed_ad.save()

    except Exception as e:
        logging.error(e)
        return JsonResponse(
            SimpleFailResponse(success=False, reason="Error getting Ad.").model_dump(),
            status=500,
        )

    return JsonResponse(
        GetAdLinkResponse(
            success=True,
            file_link=will_be_exposed_ad.file_link,
        ).model_dump(),
        status=200,
    )
