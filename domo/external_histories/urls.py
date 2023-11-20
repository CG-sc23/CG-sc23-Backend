from django.urls import path
from external_histories import views as external_history

urlpatterns = [
    path(
        "v1/github/check",
        external_history.GithubAccountCheck.as_view(),
        name="github_account_check",
    ),
    path(
        "v1/github/status/<int:user_id>",
        external_history.GithubUpdateStatus.as_view(),
        name="get_github_update_status",
    ),
    path(
        "v1/github/stack",
        external_history.GithubStack.as_view(),
        name="get_github_stack",
    ),
    path(
        "v1/github/stack/<int:user_id>",
        external_history.PublicGithubStack.as_view(),
        name="get_public_github_stack",
    ),
    path(
        "v1/github/keyword",
        external_history.GithubKeyword.as_view(),
        name="get_github_keyword",
    ),
    path(
        "v1/github/keyword/<int:user_id>",
        external_history.PublicGithubKeyword.as_view(),
        name="get_public_github_keyword",
    ),
    path(
        "v1/github/update",
        external_history.GithubManualUpdate.as_view(),
        name="github_manual_update",
    ),
    path(
        "v1/common/stack/<str:stack>",
        external_history.CommonStack.as_view(),
        name="common_stack_check",
    ),
]
