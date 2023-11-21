import logging

from common.const import ReturnCode
from common.http_model import SimpleFailResponse
from common.s3.handler import GeneralHandler
from django.http import JsonResponse
from resources.http_model import GetPreSignedUrlResponse
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


class PreSignedUrl(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get(self, request, file_name):
        type = request.GET.get("type", None)
        if not type:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )
        s3_handler = GeneralHandler(type, request.user.email)
        aws_response = s3_handler.create_presigned_url(file_name)

        if aws_response[0] == ReturnCode.INVALID_ACCESS:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )
        if aws_response[0] == ReturnCode.FAILED_CREATE_PRESIGNED_URL:
            logging.error(aws_response[1])
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Error generating presigned url."
                ).model_dump(),
                status=500,
            )
        url = f"{aws_response[1]['url']}{aws_response[1]['fields']['key']}"

        response = GetPreSignedUrlResponse(
            success=True, url=url, aws_response=aws_response[1]
        )

        return JsonResponse(
            response.model_dump(),
            status=200,
        )
