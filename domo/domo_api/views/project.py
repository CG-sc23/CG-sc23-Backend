import logging
from datetime import datetime, timezone

from django.db.transaction import atomic
from django.http import JsonResponse
from domo_api.http_model import (
    CreateProjectRequest,
    CreateProjectResponse,
    SimpleFailResponse,
)
from domo_api.models import Project, ProjectMember
from pydantic import ValidationError
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


@atomic
def create_new_project(request_user, request_data):
    new_project = Project(
        owner=request_user,
        title=request_data.title,
        short_description=request_data.short_description,
        description=request_data.description,
        created_at=datetime.now(tz=timezone.utc),
        is_public=request_data.is_public,
    )
    new_project.save()

    ProjectMember(
        project=new_project,
        user=request_user,
        role="OWNER",
        created_at=datetime.now(tz=timezone.utc),
    ).save()

    return new_project


class Info(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        title = request.data.get("title")
        short_description = request.data.get("short_description")
        description = request.data.get("description", None)
        is_public = request.data.get("is_public", None)

        try:
            request_data = CreateProjectRequest(
                title=title,
                short_description=short_description,
                description=description,
                is_public=is_public,
            )
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        try:
            new_project = create_new_project(request.user, request_data)
        except Exception as e:
            logging.error(e)
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Error creating project."
                ).model_dump(),
                status=500,
            )

        return JsonResponse(
            CreateProjectResponse(
                success=True,
                project_id=new_project.id,
                status=new_project.status,
                is_public=new_project.is_public,
                title=new_project.title,
                short_description=new_project.short_description,
                description=new_project.description,
                created_at=new_project.created_at,
            ).model_dump(),
            status=201,
        )
