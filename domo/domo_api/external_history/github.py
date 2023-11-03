import json
import os

import requests
from domo_api.models import User, UserStack


class LoadGithubHistory:
    def update_github_history(self, user_id):
        token = os.environ.get("GITHUB_API_TOKEN")

        headers = {"Authorization": "token " + token}

        user = User.objects.filter(id=user_id).get()

        github_link = user.github_link

        if not github_link:
            return "No github url"

        account = (
            github_link.split("/")[-1]
            if not github_link.split("/")[-1] == ""
            else github_link.split("/")[-2]
        )

        try:
            check_url = "https://api.github.com/users/" + account
            response = requests.get(url=check_url, headers=headers)
        except:
            return "Github API server doesn't response"

        if response.status_code != 200:
            return "Can't find github account."

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

        return "success"

    def insert_user_stack(self, user_id, language, code_amount):
        try:
            user_stack = UserStack.objects.filter(user_id=user_id, language=language)
            original_value = user_stack.get().code_amount
            user_stack.update(code_amount=original_value + code_amount)
            user_stack.save()

        except UserStack.DoesNotExist:
            UserStack(user_id)
            user_stack = UserStack(
                user_id=user_id, language=language, code_amount=code_amount
            )
            user_stack.save()
