import requests
from celery import task, shared_task
from django.db import transaction
from reminder.models import GitRepo, GitHubAccountInfo
from reminder.utility import get_requested_reviewers, send_email_logic


@shared_task()
def create_repos(username):
    """
    :param username: username of the user for which repos need to be created
    :return: None

    DO NOT USE UNIVERSAL_TOKEN HERE
    """
    git_account = GitHubAccountInfo.objects.get(username=username)
    token = git_account.token
    url = F'https://api.github.com//users/{username}/repos'
    headers = {
        'content-type': 'application/json'
    }
    if token:
        """
        the url below will only work with token. Hence this is the only way to get private repos.
        The above url will only give public repos even if you pass in the token.
        """
        url = 'https://api.github.com/user/repos'
        headers.update({'Authorization': F'token {token}'})

    req = requests.get(url, headers=headers)
    objects = []

    if req.status_code == 200:
        for i in req.json():
            objects.append(
                GitRepo(user_id=git_account.id, name=i['name'], is_private=i['private'])
            )

        with transaction.atomic():
            GitRepo.objects.bulk_create(objects)
    return


@task()
def send_reminders():
    """
    This will send reminders to the user who has email subscriptions turned on
    :return:
    """

    git_repo = GitRepo.objects.select_related('user').filter(user__email_subscription=True)
    git_repo_data = (
        get_requested_reviewers(i.user.username, i.name,  i.user.token) for i in git_repo
    )
    for i in git_repo_data:
        for j in i:
            send_email_logic(j)
    return 'done'
