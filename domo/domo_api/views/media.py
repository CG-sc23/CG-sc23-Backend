import logging

from django.http import JsonResponse
from domo_api.const import ReturnCode
from domo_api.http_model import GetPreSignedUrlResponse, SimpleFailResponse
from domo_api.s3.handler import GeneralHandler
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


class PreSignedUrl(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, file_name):
        s3_general_handler = GeneralHandler()
        aws_response = s3_general_handler.create_presigned_url(file_name)

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
