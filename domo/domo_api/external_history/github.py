import os
from datetime import datetime, timezone

import requests
from django.db.transaction import atomic
from domo_api.const import ReturnCode
from domo_api.models import GithubStatus, User, UserStack


class LoadGithubHistory:
    @atomic
    async def update_github_history(self, user_id, github_link):
        token = os.environ.get("GITHUB_API_TOKEN")

        headers = {"Authorization": "token " + token}

        github_status = GithubStatus.objects.filter(user_id=user_id)

        UserStack.objects.filter(user_id=user_id).delete()

        if not github_link:
            github_status.update(
                status=ReturnCode.GITHUB_STATS_FAILED,
                last_update=datetime.now(tz=timezone.utc),
            )
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
            github_status.update(
                status=ReturnCode.GITHUB_STATS_FAILED,
                last_update=datetime.now(tz=timezone.utc),
            )
            return ReturnCode.NO_GITHUB_URL

        if response.status_code != 200:
            github_status.update(
                status=ReturnCode.GITHUB_STATS_FAILED,
                last_update=datetime.now(tz=timezone.utc),
            )
            return ReturnCode.CANNOT_FIND_GITHUB_ACCOUNT

        user_data = response.json()

        repos_url = user_data.get("repos_url")

        user_repos = requests.get(url=repos_url, headers=headers).json()

        for repo in user_repos:
            language_url = (
                "https://api.github.com/repos/"
                + account
                + "/"
                + repo.get("name")
                + "/languages"
            )

            user_language = requests.get(url=language_url, headers=headers).json()

            for language, code_amount in user_language.items():
                self.insert_user_stack(
                    user_id=user_id, language=language, code_amount=code_amount
                )

        github_status.update(
            status=ReturnCode.GITHUB_STATUS_COMPLETE,
            last_update=datetime.now(tz=timezone.utc),
        )

        return ReturnCode.HISTORY_UPDATE_SUCCESS

    @atomic
    def insert_user_stack(self, user_id, language, code_amount):
        try:
            user_stack = UserStack.objects.filter(user_id=user_id, language=language)
            original_value = user_stack.get().code_amount
            user_stack.update(code_amount=original_value + code_amount)
            user_stack.save()

        except UserStack.DoesNotExist:
            user_stack = UserStack(
                user_id=user_id, language=language, code_amount=code_amount
            )
            user_stack.save()
