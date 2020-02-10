from reminder.models import GitHubAccountInfo
from rest_framework import serializers
from remindGit.settings import UNIVERSAL_GITHUB_TOKEN
import requests

EMAIL_ERRORS = {
    "invalid": "Enter Valid email address",
    "blank": "Please provide email"
}
USERNAME_ERRORS = {
    "blank": "Please provide username"
}


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, max_length=100, error_messages=USERNAME_ERRORS)
    email = serializers.EmailField(required=True, error_messages=EMAIL_ERRORS)

    class Meta:
        model = GitHubAccountInfo
        fields = '__all__'

    @staticmethod
    def validate_email(email):
        if GitHubAccountInfo.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already exists.")
        return email

    @staticmethod
    def validate_username(username):
        url = F'https://api.github.com/users/{username}'
        req = requests.get(url)
        if req.status_code != 200:
            req = requests.get(url, headers={'Authorization': F'token {UNIVERSAL_GITHUB_TOKEN}'})
            if req.status_code != 200:
                raise serializers.ValidationError('GitHub user does not exist')

        if GitHubAccountInfo.objects.filter(username=username).exists():
            raise serializers.ValidationError("Username already exists.")

        return username
