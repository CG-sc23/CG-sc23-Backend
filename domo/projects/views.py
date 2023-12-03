import json
import logging
import random
from datetime import datetime, timezone
from operator import itemgetter

from common.gpt import MilestoneGPT
from common.http_model import SimpleFailResponse, SimpleSuccessResponse
from common.s3.handler import GeneralHandler
from django.db.transaction import atomic
from django.http import JsonResponse
from external_histories.models import UserStack
from milestones.models import Milestone
from projects.http_model import (
    ChangeRoleRequest,
    CreateProjectRequest,
    CreateProjectResponse,
    GetJoinResponse,
    GetProjectAllResponse,
    GetProjectResponse,
    KickMemberRequest,
    MakeProjectInviteDetailResponse,
    MakeProjectInviteRequest,
    MakeProjectInviteResponse,
    MilestoneGPTResponse,
    ModifyProjectRequest,
    ReplyJoinRequestModel,
)
from projects.models import Project, ProjectInvite, ProjectJoinRequest, ProjectMember
from pydantic import ValidationError
from resources.models import S3ResourceReferenceCheck
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from task_groups.models import TaskGroup
from tasks.models import Task
from users.http_model import GetUserRecommendResponse
from users.models import User


@atomic
def create_new_project(request_user, request_data):
    new_project = Project(
        owner=request_user,
        title=request_data.title,
        short_description=request_data.short_description,
        description=request_data.description,
        description_resource_links=request_data.description_resource_links,
        created_at=datetime.now(tz=timezone.utc),
        due_date=request_data.due_date,
        thumbnail_image=request_data.thumbnail_image,
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
        short_description = request.data.get("short_description", None)
        description = request.data.get("description", None)
        description_resource_links = request.data.get(
            "description_resource_links", None
        )
        if description_resource_links:
            description_resource_links = json.loads(description_resource_links)

        due_date = request.data.get("due_date", None)
        thumbnail_image = request.data.get("thumbnail_image", None)

        try:
            request_data = CreateProjectRequest(
                title=title,
                short_description=short_description,
                description=description,
                description_resource_links=description_resource_links,
                due_date=due_date,
                thumbnail_image=thumbnail_image,
            )
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        request_data.due_date = request_data.due_date.replace(
            hour=14, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc
        )

        if isinstance(request_data.description_resource_links, list):
            s3_handler = GeneralHandler("resource")
            if not s3_handler.check_resource_links(
                request_data.description_resource_links
            ):
                return JsonResponse(
                    SimpleFailResponse(
                        success=False,
                        reason="Invalid request.",
                    ).model_dump(),
                    status=400,
                )
            for resource_link in request_data.description_resource_links:
                try:
                    S3ResourceReferenceCheck.objects.get(resource_link=resource_link)
                except S3ResourceReferenceCheck.DoesNotExist:
                    S3ResourceReferenceCheck.objects.create(
                        resource_link=resource_link,
                        owner=request.user,
                    )

        if thumbnail_image:
            s3_handler = GeneralHandler("resource")
            if not s3_handler.check_resource_links(request_data.thumbnail_image):
                return JsonResponse(
                    SimpleFailResponse(
                        success=False,
                        reason="Invalid thumbnail image.",
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
                id=new_project.id,
                status=new_project.status,
                title=new_project.title,
                short_description=new_project.short_description,
                description=new_project.description,
                description_resource_links=new_project.description_resource_links,
                created_at=new_project.created_at,
                due_date=new_project.due_date,
                thumbnail_image=new_project.thumbnail_image,
            ).model_dump(),
            status=201,
        )

    def put(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Can't find project."
                ).model_dump(),
                status=404,
            )

        try:
            member_role = ProjectMember.objects.get(
                project=project, user=request.user
            ).role
        except ProjectMember.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(success=False, reason="Not found").model_dump(),
                status=404,
            )

        if member_role == "MEMBER":
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="User must OWNER or MANAGER"
                ).model_dump(),
                status=403,
            )

        title = request.data.get("title", None)
        status = request.data.get("status", None)
        if not status:
            status = project.status
        short_description = request.data.get("short_description", None)
        description = request.data.get("description", None)
        description_resource_links = request.data.get(
            "description_resource_links", None
        )
        if description_resource_links:
            description_resource_links = json.loads(description_resource_links)

        due_date = request.data.get("due_date", None)
        thumbnail_image = request.data.get("thumbnail_image", None)

        try:
            request_data = ModifyProjectRequest(
                title=title,
                status=status,
                short_description=short_description,
                description=description,
                description_resource_links=description_resource_links,
                due_date=due_date,
                thumbnail_image=thumbnail_image,
            )
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        if request_data.due_date:
            request_data.due_date = request_data.due_date.replace(
                hour=14, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc
            )

        if thumbnail_image:
            s3_handler = GeneralHandler("resource")
            if not s3_handler.check_resource_links(request_data.thumbnail_image):
                return JsonResponse(
                    SimpleFailResponse(
                        success=False,
                        reason="Invalid thumbnail image.",
                    ).model_dump(),
                    status=400,
                )

        # description에 media가 있을경우, validation check가 필요하다.
        # 이후 owner를 지정한다.
        if isinstance(request_data.description_resource_links, list):
            s3_handler = GeneralHandler("resource")
            if not s3_handler.check_resource_links(
                request_data.description_resource_links
            ):
                return JsonResponse(
                    SimpleFailResponse(
                        success=False,
                        reason="Invalid request.",
                    ).model_dump(),
                    status=400,
                )
            for resource_link in request_data.description_resource_links:
                try:
                    S3ResourceReferenceCheck.objects.get(resource_link=resource_link)
                except S3ResourceReferenceCheck.DoesNotExist:
                    S3ResourceReferenceCheck.objects.create(
                        resource_link=resource_link,
                        owner=request.user,
                    )

            project_description_resource_links = project.description_resource_links
            if project_description_resource_links:
                for resource_link in project_description_resource_links:
                    ref_check_obj = S3ResourceReferenceCheck.objects.get(
                        resource_link=resource_link
                    )
                    if (
                        ref_check_obj.resource_link
                        not in request_data.description_resource_links
                        and ref_check_obj.owner == request.user
                    ):
                        ref_check_obj.delete()
                        s3_handler.remove_resource(resource_link)

        try:
            project.title = request_data.title or project.title
            project.status = request_data.status or project.status
            project.short_description = (
                request_data.short_description or project.short_description
            )
            project.description = request_data.description or project.description
            project.description_resource_links = (
                request_data.description_resource_links
                or project.description_resource_links
            )
            project.thumbnail_image = (
                request_data.thumbnail_image or project.thumbnail_image
            )
            project.due_date = request_data.due_date or project.due_date
            project.save()

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
                id=project.id,
                status=project.status,
                title=project.title,
                short_description=project.short_description,
                description=project.description,
                description_resource_links=project.description_resource_links,
                created_at=project.created_at,
                due_date=project.due_date,
                thumbnail_image=project.thumbnail_image,
            ).model_dump(),
            status=200,
        )

    def delete(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Can't find project."
                ).model_dump(),
                status=404,
            )

        try:
            member_role = ProjectMember.objects.get(
                project=project, user=request.user
            ).role
        except ProjectMember.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(success=False, reason="Not found").model_dump(),
                status=404,
            )

        if member_role != "OWNER":
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="User must OWNER"
                ).model_dump(),
                status=403,
            )

        try:
            milestones = Milestone.objects.filter(project_id=project.id)
            for milestone in milestones:
                task_groups = TaskGroup.objects.filter(milestone_id=milestone.id)
                for task_group in task_groups:
                    tasks_cnt = Task.objects.filter(task_group_id=task_group.id).count()
                    if tasks_cnt > 0:
                        return JsonResponse(
                            SimpleFailResponse(
                                success=False,
                                reason="This project has tasks. Please delete all tasks.",
                            ).model_dump(),
                            status=400,
                        )
        except Exception as e:
            logging.error(e)
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Error deleting project."
                ).model_dump(),
                status=500,
            )

        try:
            s3_handler = GeneralHandler("resource")
            project_description_resource_links = project.description_resource_links
            if project_description_resource_links:
                for resource_link in project_description_resource_links:
                    ref_check_obj = S3ResourceReferenceCheck.objects.get(
                        resource_link=resource_link
                    )
                    ref_check_obj.delete()
                    s3_handler.remove_resource(resource_link)
            if project.thumbnail_image:
                ref_check_obj = S3ResourceReferenceCheck.objects.get(
                    resource_link=project.thumbnail_image
                )
                ref_check_obj.delete()
                s3_handler.remove_resource(project.thumbnail_image)

            project.delete()

        except Exception as e:
            logging.error(e)
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Error deleting project."
                ).model_dump(),
                status=500,
            )

        return JsonResponse(
            SimpleSuccessResponse(
                success=True,
            ).model_dump(),
            status=200,
        )


class PublicInfo(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Can't find project."
                ).model_dump(),
                status=404,
            )

        try:
            member_role = ProjectMember.objects.get(
                project=project, user=request.user
            ).role
        except:
            member_role = "NOTHING"

        owner_data = {
            "id": project.owner.id,
            "email": project.owner.email,
            "name": project.owner.name,
            "profile_image_link": project.owner.profile_image_link,
            "profile_image_updated_at": project.owner.profile_image_updated_at,
        }

        milestones = Milestone.objects.filter(project_id=project.id)
        milestones_data = []
        for milestone in milestones:
            milestones_data.append(milestone.simple_info())

        project_members = ProjectMember.objects.filter(project=project)

        project_member_datas = []

        for member in project_members:
            project_member_data = {
                "id": member.user.id,
                "name": member.user.name,
                "email": member.user.email,
                "profile_image_link": member.user.profile_image_link,
                "profile_image_updated_at": member.user.profile_image_updated_at,
            }

            project_member_datas.append(project_member_data)

        return JsonResponse(
            GetProjectResponse(
                success=True,
                owner=owner_data,
                id=project.id,
                status=project.status,
                title=project.title,
                short_description=project.short_description,
                description=project.description,
                description_resource_links=project.description_resource_links,
                created_at=project.created_at,
                due_date=project.due_date,
                thumbnail_image=project.thumbnail_image,
                milestones=milestones_data,
                members=project_member_datas,
                permission=member_role,
            ).model_dump(),
            status=200,
        )


class Invite(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @atomic
    def post(self, request):
        project_id = request.data.get("project_id")
        invitee_emails = json.loads(request.data.get("invitee_emails"))
        try:
            request_data = MakeProjectInviteRequest(
                project_id=project_id,
                invitee_emails=invitee_emails,
            )
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        if not Project.objects.filter(
            id=request_data.project_id,
        ).exists():
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Project does not exist."
                ).model_dump(),
                status=404,
            )

        if not ProjectMember.objects.filter(
            project_id=project_id, user_id=request.user.id
        ).exists():
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="You are not in requested project."
                ).model_dump(),
                status=403,
            )

        result = []
        for invitee_email in request_data.invitee_emails:
            if not User.objects.filter(email=invitee_email).exists():
                result.append(
                    MakeProjectInviteDetailResponse.create(
                        invitee_email, False, "User does not exist."
                    )
                )
            elif ProjectMember.objects.filter(
                project__id=project_id, user__email=invitee_email
            ).exists():
                result.append(
                    MakeProjectInviteDetailResponse.create(
                        invitee_email, False, "User already in project."
                    )
                )
            else:
                try:
                    invitee_id = User.objects.get(email=invitee_email).id
                    if not ProjectInvite.objects.filter(
                        project_id=project_id,
                        inviter_id=request.user.id,
                        invitee_id=invitee_id,
                    ).exists():
                        ProjectInvite(
                            project_id=project_id,
                            inviter_id=request.user.id,
                            invitee_id=invitee_id,
                            created_at=datetime.now(tz=timezone.utc),
                        ).save()
                except Exception as e:
                    logging.error(e)
                    return JsonResponse(
                        SimpleFailResponse(
                            success=False, reason="Error inviting user."
                        ).model_dump(),
                        status=500,
                    )
                result.append(
                    MakeProjectInviteDetailResponse.create(invitee_email, True)
                )

        return JsonResponse(
            MakeProjectInviteResponse(result=result).model_dump(),
            status=200,
        )


class Role(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, project_id):
        user_email = request.data.get("user_email")
        role = request.data.get("role")

        try:
            request_data = ChangeRoleRequest(
                user_email=user_email,
                role=role,
            )
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(success=False, reason="Not Found.").model_dump(),
                status=404,
            )

        try:
            member_role = ProjectMember.objects.get(
                project=project, user=request.user
            ).role
        except ProjectMember.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="You are not in requested project."
                ).model_dump(),
                status=403,
            )

        if member_role == "MEMBER":
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="You must OWNER or MANAGER."
                ).model_dump(),
                status=403,
            )

        if role not in ["MANAGER", "MEMBER"]:
            return JsonResponse(
                SimpleFailResponse(success=False, reason="Invalid role.").model_dump(),
                status=400,
            )

        if not ProjectMember.objects.filter(
            project_id=project_id, user__email=request_data.user_email
        ).exists():
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Requested user does not exist in project."
                ).model_dump(),
                status=404,
            )

        if (
            ProjectMember.objects.get(
                project_id=project_id, user__email=request_data.user_email
            ).role
            == "OWNER"
        ):
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="You can't change owner's role."
                ).model_dump(),
                status=403,
            )
        try:
            user_obj = ProjectMember.objects.get(
                project_id=project_id, user__email=request_data.user_email
            )
            user_obj.role = request_data.role
            user_obj.save()
        except Exception as e:
            logging.error(e)
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Error changing role."
                ).model_dump(),
                status=500,
            )

        return JsonResponse(
            SimpleSuccessResponse(success=True).model_dump(),
            status=200,
        )


class AllInfo(APIView):
    def get(self, request):
        projects = Project.objects.filter().order_by("-created_at")

        project_datas = []

        for project in projects:
            project_members = ProjectMember.objects.filter(project=project)

            project_member_datas = []

            for member in project_members:
                project_member_data = {
                    "id": member.user.id,
                    "name": member.user.name,
                    "email": member.user.email,
                    "profile_image_link": member.user.profile_image_link,
                    "profile_image_updated_at": member.user.profile_image_updated_at,
                }

                project_member_datas.append(project_member_data)

            project_data = {
                "id": project.id,
                "title": project.title,
                "status": project.status,
                "created_at": project.created_at,
                "due_date": project.due_date,
                "thumbnail_image": project.thumbnail_image,
                "short_description": project.short_description,
                "members": project_member_datas,
            }

            project_datas.append(project_data)

        return JsonResponse(
            GetProjectAllResponse(
                success=True, count=len(project_datas), projects=project_datas
            ).model_dump(),
            status=200,
        )


class RecommendUserForProject(APIView):  # pragma: no cover
    def recommend_user(self, users, request_project):
        all_user = []

        for user in users:
            all_user.append(user)

        project_members = ProjectMember.objects.filter(project=request_project)

        stacks_avg = 0

        for member in project_members:
            stacks = UserStack.objects.filter(user=member.user)

            for stack in stacks:
                stacks_avg += stack.code_amount

        stacks_avg /= project_members.count()

        similarity = []

        for user in all_user:
            stacks = UserStack.objects.filter(user=user)

            user_stacks_sum = 0
            for stack in stacks:
                user_stacks_sum += stack.code_amount

            ratio = abs(user_stacks_sum - stacks_avg)
            similarity.append({"user": user, "ratio": ratio})

        sorted_data = sorted(similarity, key=itemgetter("ratio"))

        recommended_user = []

        for data in sorted_data:
            if len(recommended_user) >= 6:
                break
            recommended_user.append(data["user"])

        return recommended_user

    def get(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Can't find project."
                ).model_dump(),
                status=404,
            )

        users = User.objects.filter(is_staff=False, is_active=True).exclude(
            projectmember__project=project
        )

        recommended_users = self.recommend_user(users, project)

        user_datas = []

        for user in recommended_users:
            user_data = {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "profile_image_link": user.profile_image_link,
                "profile_image_updated_at": user.profile_image_updated_at,
                "short_description": user.short_description,
            }

            user_datas.append(user_data)

        result = GetUserRecommendResponse(
            success=True, count=len(user_datas), users=user_datas
        )
        return JsonResponse(
            result.model_dump(),
            status=200,
        )


class RecommendProject(APIView):  # pragma: no cover
    authentication_classes = [TokenAuthentication]

    def recommend_project_public(self, projects):
        all_project = []

        for project in projects:
            all_project.append(project)

        count = 6

        if len(all_project) < 6:
            count = len(all_project)

        recommended_project = random.sample(all_project, count)

        return recommended_project

    def recommend_project(self, projects, request_user):
        stacks = UserStack.objects.filter(user=request_user)

        user_stacks_sum = 0
        for stack in stacks:
            user_stacks_sum += stack.code_amount

        similarity = []

        for project in projects:
            project_members = ProjectMember.objects.filter(project=project)

            stacks_avg = 0

            for member in project_members:
                stacks = UserStack.objects.filter(user=member.user)

                for stack in stacks:
                    stacks_avg += stack.code_amount

            stacks_avg /= project_members.count()
            ratio = abs(user_stacks_sum - stacks_avg)
            similarity.append({"project": project, "ratio": ratio})

        sorted_data = sorted(similarity, key=itemgetter("ratio"))

        recommended_project = []

        for data in sorted_data:
            if len(recommended_project) >= 6:
                break
            recommended_project.append(data["project"])

        return recommended_project

    def get(self, request):
        try:
            projects = Project.objects.exclude(projectmember__user=request.user)
            recommended_project = self.recommend_project(projects, request.user)
        except:
            projects = Project.objects.all()
            recommended_project = self.recommend_project_public(projects)

        project_datas = []

        for project in recommended_project:
            project_members = ProjectMember.objects.filter(project=project)

            project_member_datas = []

            for member in project_members:
                project_member_data = {
                    "id": member.user.id,
                    "name": member.user.name,
                    "email": member.user.email,
                    "profile_image_link": member.user.profile_image_link,
                    "profile_image_updated_at": member.user.profile_image_updated_at,
                }

                project_member_datas.append(project_member_data)

            project_data = {
                "id": project.id,
                "title": project.title,
                "status": project.status,
                "created_at": project.created_at,
                "due_date": project.due_date,
                "thumbnail_image": project.thumbnail_image,
                "short_description": project.short_description,
                "members": project_member_datas,
            }

            project_datas.append(project_data)

        return JsonResponse(
            GetProjectAllResponse(
                success=True, count=len(project_datas), projects=project_datas
            ).model_dump(),
            status=200,
        )


class Kick(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, project_id):
        user_email = request.GET.get("user_email")

        try:
            request_data = KickMemberRequest(user_email=user_email)
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        try:
            requester = ProjectMember.objects.get(
                project_id=project_id, user=request.user
            )
            will_kick_member = ProjectMember.objects.get(
                project_id=project_id, user__email=request_data.user_email
            )
        except ProjectMember.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(success=False, reason="Not Found.").model_dump(),
                status=404,
            )

        if requester.role == "MEMBER":
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="You must OWNER or MANAGER."
                ).model_dump(),
                status=403,
            )

        if will_kick_member.role == "OWNER":
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="You can't kick owner."
                ).model_dump(),
                status=403,
            )

        try:
            will_kick_member.delete()
        except Exception as e:
            logging.error(e)
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Error kicking member."
                ).model_dump(),
                status=500,
            )

        return JsonResponse(
            SimpleSuccessResponse(success=True).model_dump(),
            status=200,
        )


class MakeJoinRequest(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        try:
            user = ProjectMember.objects.get(project_id=project_id, user=request.user)
            if user.role == "MEMBER":
                raise ProjectMember.DoesNotExist
        except ProjectMember.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=403,
            )

        join_requests = ProjectJoinRequest.objects.filter(project_id=project_id)
        join_request_datas = []

        for join_request in join_requests:
            join_request_data = {
                "id": join_request.id,
                "user": {
                    "id": join_request.user.id,
                    "name": join_request.user.name,
                    "email": join_request.user.email,
                    "profile_image_link": join_request.user.profile_image_link,
                    "profile_image_updated_at": join_request.user.profile_image_updated_at,
                },
                "message": join_request.message,
                "created_at": join_request.created_at,
            }
            join_request_datas.append(join_request_data)

        return JsonResponse(
            GetJoinResponse(success=True, result=join_request_datas).model_dump(),
            status=200,
        )

    def post(self, request, project_id):
        message = request.data.get("message")
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Project does not exist."
                ).model_dump(),
                status=404,
            )

        if ProjectMember.objects.filter(
            project_id=project_id, user_id=request.user.id
        ).exists():
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="You are already in project."
                ).model_dump(),
                status=400,
            )
        try:
            if not ProjectJoinRequest.objects.filter(
                project_id=project_id, user_id=request.user.id
            ).exists():
                ProjectJoinRequest(
                    project=project,
                    user=request.user,
                    message=message,
                    created_at=datetime.now(tz=timezone.utc),
                ).save()
        except Exception as e:
            logging.error(e)
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Error requesting join."
                ).model_dump(),
                status=500,
            )

        return JsonResponse(
            SimpleSuccessResponse(success=True).model_dump(),
            status=200,
        )


class ReplyJoinRequest(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        join_request_id = request.data.get("join_request_id")
        accept = request.data.get("accept")

        data_dict = {
            "join_request_id": join_request_id,
            "accept": accept,
        }

        try:
            request_data = ReplyJoinRequestModel(**data_dict)
        except ValidationError:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=400,
            )

        try:
            join_request_obj = ProjectJoinRequest.objects.get(
                id=request_data.join_request_id
            )
            user = ProjectMember.objects.get(
                project=join_request_obj.project, user=request.user
            )
            if user.role == "MEMBER":
                raise ProjectMember.DoesNotExist
        except (ProjectJoinRequest.DoesNotExist, ProjectMember.DoesNotExist):
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Invalid request."
                ).model_dump(),
                status=403,
            )

        if request_data.accept:
            if ProjectMember.objects.filter(
                project=join_request_obj.project, user=join_request_obj.user
            ).exists():
                return JsonResponse(
                    SimpleSuccessResponse(success=True).model_dump(),
                    status=200,
                )

            ProjectMember.objects.create(
                project=join_request_obj.project,
                user=join_request_obj.user,
                role="MEMBER",
                created_at=datetime.now(tz=timezone.utc),
            )
        join_request_obj.delete()

        return JsonResponse(
            SimpleSuccessResponse(success=True).model_dump(),
            status=200,
        )


class MakeMilestoneByGPT(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="Project does not exist."
                ).model_dump(),
                status=404,
            )

        try:
            member = ProjectMember.objects.get(project=project, user=request.user)
            if member.role == "MEMBER":
                raise ProjectMember.DoesNotExist
        except ProjectMember.DoesNotExist:
            raise PermissionError

        gpt_query = {"project_description": project.description}
        exist_milestones = Milestone.objects.filter(project=project)
        if not exist_milestones:
            gpt_query["milestones"] = []
        else:
            gpt_query["milestones"] = [
                {"title": milestone.subject, "tags": milestone.tags}
                for milestone in exist_milestones
            ]

        raw_gpt_result = MilestoneGPT(json.dumps(gpt_query)).get_response()

        try:
            if raw_gpt_result in ["'CANT_UNDERSTAND'", "CANT_UNDERSTAND"]:
                raise ValidationError
            json_data = json.loads(raw_gpt_result)
            gpt_result = MilestoneGPTResponse(
                title=json_data["title"], tags=json_data["tags"]
            )
        except Exception as e:
            logging.error(e)
            return JsonResponse(
                SimpleFailResponse(
                    success=False, reason="GPT response is invalid."
                ).model_dump(),
                status=500,
            )

        return JsonResponse(
            MilestoneGPTResponse(
                success=True,
                title=gpt_result.title,
                tags=gpt_result.tags,
            ).model_dump(),
            status=200,
        )
