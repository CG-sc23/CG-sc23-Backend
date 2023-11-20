# Create your tasks here
import os
from collections import defaultdict
from datetime import datetime, timezone

import requests
from celery import shared_task
from common.const import ReturnCode, ReturnList
from django.db.transaction import atomic
from external_histories.models import GithubStatus, UserKeyword, UserStack
from users.models import User

words = defaultdict(lambda: 0)


@shared_task
@atomic
def update_github_history(user_id, github_link):
    token = os.environ.get("GITHUB_API_TOKEN")

    headers = {"Authorization": "Bearer " + token}

    global words
    words = defaultdict(lambda: 0)

    github_status = GithubStatus.objects.get(user_id=user_id)

    UserStack.objects.filter(user_id=user_id).delete()

    UserKeyword.objects.filter(user_id=user_id).delete()

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

        dependency_url = (
            f"https://api.github.com/repos/{account}/"
            f"{repo.get('name')}/dependency-graph/sbom"
        )

        user_dependency = requests.get(url=dependency_url, headers=headers).json()

        insert_user_dependency(dependency=user_dependency)

    sorted_words = sorted(words.items(), key=lambda x: x[1], reverse=True)

    i = 0
    word_list = ReturnList.WORD_LIST
    for word in sorted_words:
        if i == 20:
            break
        # word is tuple (word, count)
        if word[0] not in word_list:
            continue

        i += 1
        user_keyword = UserKeyword(user_id=user_id, keyword=word[0], count=word[1])
        user_keyword.save()

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


@atomic
def insert_user_dependency(dependency):
    def word_count(string):
        string = (
            string.replace(" ", ".")
            .replace("-", ".")
            .replace(":", ".")
            .replace("/", ".")
            .replace("@", ".")
        )
        string_set = string.split(".")

        for word in string_set:
            words[word] += 1

    if type(dependency) is not dict:
        return
    for key, value in dependency.items():
        if key == "name":
            word_count(value)
        elif type(value) is dict:
            insert_user_dependency(value)
        elif type(value) is list:
            for item in value:
                insert_user_dependency(item)


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
        else:
            github_status = GithubStatus.objects.get(user=user)
            if github_status.status == ReturnCode.GITHUB_STATUS_IN_PROGRESS:
                continue
            github_status.status = ReturnCode.GITHUB_STATUS_IN_PROGRESS
            github_status.last_update = datetime.now(tz=timezone.utc)
            github_status.save()

        update_github_history(user.id, user.github_link)


@shared_task
def periodic_fail_check_github_history():
    users = GithubStatus.objects.filter(status=ReturnCode.GITHUB_STATUS_IN_PROGRESS)

    for user in users:
        if (datetime.now(tz=timezone.utc) - user.last_update).total_seconds() > 60 * 30:
            user.status = ReturnCode.GITHUB_STATUS_FAILED
            user.last_update = datetime.now(tz=timezone.utc)
            user.save()
