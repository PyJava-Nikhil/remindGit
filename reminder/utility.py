import requests
from datetime import datetime
from remindGit.settings import (
    EMAIL_INTERVAL,
)
from django.core.mail import send_mail
from reminder.models import Reminder, GitRepo, GitHubAccountInfo
from django.db import transaction
from django.utils import timezone


def list_pulls(username, repo, token=None):

    """
    :param username: username of the user for which pulls need to be listed
    :param repo: repo for which pulls should be listed
    :param token: Pass the token into the headers to make a authenticated request to GitHub API;
        Otherwise only public data can be pulled.
    :return: requests object which will have the required data to work upon
    """
    url = F'https://api.github.com/repos/{username}/{repo}/pulls?state=open'
    headers = {'content-type': 'application/json'}

    if token:
        headers.update({'Authorization': F'token {token}'})

    req = requests.get(url, headers=headers)
    return req


def get_requested_reviewers(username, repo, token=None):
    """
    :param username: username of the GitHub account
    :param repo: repo name
    :param token: token of the user
    :return: Return a list to send email to user regarding each repo the user
    has been asked to review the PR's
    """

    pulls = list_pulls(username, repo, token).json()
    data = []
    for i in pulls:
        for j in i['requested_reviewers']:
            if j['login'] == username:
                body = {
                    'url': i['url'],
                    'pr_id': i['id'],
                    'created_at': i['created_at'],
                    'updated_at': i['updated_at'],
                    'username': username,
                    'repo': repo,
                    'number': i['number']
                }
                data.append(body)
                break
    return data


# def get_comments(username, repo, token=None):
#     """
#     :param username: username of the GitHub account
#     :param repo: repo name with Username attached
#     :param token: token of the user
#     :return: return the data for the comment
#     """


def send_email_logic(data, email_subject='RR'):
    """
    Send email to user on the basis of last email sent to him/her on the basis of
    reminder.models.Reminder or on the basis of last_update of the PR.
    Current interval will be set globally in settings.py for now.
    :param data: data will contain data related to send email data
    :param email_subject: email needs to be sent for what purpose
    :return: Maybe email sent status
    """

    pr_id = data['pr_id']
    username = data['username']
    git_repo = GitRepo.objects.get(name=data['repo'], user__username=username)
    user_email, user_id, repo_id = git_repo.user.email, git_repo.user_id, git_repo.id
    subject = 'Requested Review Pending' if email_subject == 'RR' else 'Resolve comments Reminder'
    body = (
        F'Please review the PR {data["url"]}' if email_subject == 'RR' else
        F'Please resolve the comments on the PR {data["url"]}. Directly go to the comments'
    )
    reminder = Reminder.objects.filter(pr_id=pr_id, reminder_type=email_subject).order_by('-email_time')
    if reminder.exists():
        date_time = reminder.first().email_time
    else:
        date, time = data['created_at'].split('T')
        time = time[0:-1]
        date_time = F'{date} {time}'
        date_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')

    seconds = (timezone.now() - date_time).seconds
    if seconds > EMAIL_INTERVAL:
        with transaction.atomic():
            send_mail(subject, body, 'nikhilglo122@gmail.com', [user_email], fail_silently=False)
            Reminder.objects.create(
                repo_id=repo_id, reviewer_id=user_id, email_time=timezone   .now(),
                reminder_type=email_subject, text_body=body,
                pr_id=pr_id,
            )

    return 'Done'
