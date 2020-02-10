from django.db import models
# Create your models here.


class GitHubAccountInfo(models.Model):
    """
    This model will hold the access token for the user with other info
    """

    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=256, unique=True)
    token = models.CharField(
        max_length=100, null=True, blank=True,
        help_text="this token will be GitHub user's personal token. Hence user will create the same"
                  "at his/her side."
    )
    email_subscription = models.BooleanField(default=True, help_text="toggle this On/Off for email reminders.")

    class Meta:
        unique_together = [['username', 'email']]

    def __str__(self):
        return self.username


class GitRepo(models.Model):
    """
    This model will hold the repo's for the user
    """
    user = models.ForeignKey(
        GitHubAccountInfo, related_name='git_repo', on_delete=models.CASCADE,
        null=True, blank=True
    )
    name = models.CharField(max_length=100, null=True, blank=True, help_text='repo_name')
    is_private = models.BooleanField(default=False, help_text="whether the repo is public/private")

    def __str__(self):
        return F'{self.name} {self.user.username}'

    @property
    def repo_url(self):
        # use this property to attach to the URL for GitHub
        return F'{self.user.username}/{self.name}'


# class PRData(models.Model):
#     """
#     PR related data
#     """
#     repo = models.ForeignKey(
#         GitRepo, related_name='pr_repo', on_delete=models.CASCADE,
#         null=True, blank=True
#     )
#     reviewer = models.ForeignKey(
#         GitHubAccountInfo, related_name='pr_reviewer', on_delete=models.CASCADE,
#         null=True, blank=True
#     )
#     pr_id = models.CharField(max_length=500, null=True, blank=True, help_text="GitHub PR ID")
#     pr_number = models.CharField(max_length=500, null=True, blank=True, help_text='PR NUMBER')


class Reminder(models.Model):
    """
    This will store the last_email reminder for the reviewer for both comments and PR requested
    reviews.
    """
    EVENTS = (
        ('CM', 'COMMENTS'),
        ('RR', 'REQUESTED_REVIEWS')
    )
    repo = models.ForeignKey(
        GitRepo, related_name='reminder_repo', on_delete=models.CASCADE,
        null=True, blank=True
    )
    reviewer = models.ForeignKey(
        GitHubAccountInfo, related_name='reminder_reviewer', on_delete=models.CASCADE,
        null=True, blank=True
    )
    email_time = models.DateTimeField(null=True, blank=True, help_text='last time email sent to the user')
    reminder_type = models.CharField(max_length=2, choices=EVENTS, null=True, blank=True)
    text_body = models.TextField(null=True, blank=True)
    pr_id = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return F'{self.reviewer.username} {self.reminder_type}'
