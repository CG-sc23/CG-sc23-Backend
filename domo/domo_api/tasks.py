# Create your tasks here
import os
from datetime import datetime, timezone

import requests
from celery import shared_task
from django.db.transaction import atomic
from domo_api.const import ReturnCode
from domo_api.models import GithubStatus, User, UserStack


@shared_task
@atomic
def update_github_history(user_id, github_link):
    token = os.environ.get("GITHUB_API_TOKEN")

    headers = {"Authorization": "Bearer " + token}

    github_status = GithubStatus.objects.get(user_id=user_id)

    UserStack.objects.filter(user_id=user_id).delete()

    if not github_link:
        github_status.status = ReturnCode.GITHUB_STATUS_FAILED
        github_status.last_update = datetime.now(tz=timezone.utc)
        github_status.save()
        return ReturnCode.NO_GITHUB_URL

    account = (
        github_link.split("/")[-1]
        if not github_link.split("/")[-1] == ""
        else github_link.split("/")[-2]
    )

    try:
        check_url = "https://api.github.com/users/" + account
        response = requests.get(url=check_url, headers=headers)
    except:
        github_status.status = ReturnCode.GITHUB_STATUS_FAILED
        github_status.last_update = datetime.now(tz=timezone.utc)
        github_status.save()
        return ReturnCode.NO_GITHUB_URL

    if response.status_code != 200:
        github_status.status = ReturnCode.GITHUB_STATUS_FAILED
        github_status.last_update = datetime.now(tz=timezone.utc)
        github_status.save()
        return ReturnCode.CANNOT_FIND_GITHUB_ACCOUNT

    user_data = response.json()

    repos_url = user_data.get("repos_url")

    user_repos = requests.get(url=repos_url, headers=headers).json()

    for repo in user_repos:
        language_url = (
            f"https://api.github.com/repos/{account}/" f"{repo.get('name')}/languages"
        )

        user_language = requests.get(url=language_url, headers=headers).json()

        for language, code_amount in user_language.items():
            insert_user_stack(
                user_id=user_id, language=language, code_amount=code_amount
            )

    github_status.status = ReturnCode.GITHUB_STATUS_COMPLETE
    github_status.last_update = datetime.now(tz=timezone.utc)
    github_status.save()

    return ReturnCode.HISTORY_UPDATE_SUCCESS


@atomic
def insert_user_stack(user_id, language, code_amount):
    try:
        user_stack = UserStack.objects.get(user_id=user_id, language=language)
        original_value = user_stack.code_amount
        user_stack.code_amount = original_value + code_amount
        user_stack.save()

    except UserStack.DoesNotExist:
        user_stack = UserStack(
            user_id=user_id, language=language, code_amount=code_amount
        )
        user_stack.save()


@shared_task
def periodic_update_github_history():
    users = User.objects.filter(github_link__isnull=False)
    for user in users:
        if not GithubStatus.objects.filter(user=user).exists():
            github_status = GithubStatus(
                user=user,
                status=ReturnCode.GITHUB_STATUS_IN_PROGRESS,
                last_update=datetime.now(tz=timezone.utc),
            )
            github_status.save()

        update_github_history(user, user.github_link)


@shared_task
def periodic_fail_check_github_history():
    users = GithubStatus.objects.filter(status=ReturnCode.GITHUB_STATUS_IN_PROGRESS)

    for user in users:
        if (datetime.now(tz=timezone.utc) - user.last_update).total_seconds() > 60 * 30:
            user.status = ReturnCode.GITHUB_STATUS_FAILED
            user.last_update = datetime.now(tz=timezone.utc)
            user.save()
