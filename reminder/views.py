from rest_framework.views import APIView
from rest_framework.response import Response
from reminder.serializers import RegisterSerializer
from reminder.tasks import create_repos
from django.db import transaction
# Create your views here.


class Register(APIView):
    """
    This API will be used to register/link the github of incoming user
    """
    serializer_class = RegisterSerializer

    def post(self, request):
        """
        :param request:  Will have
            email: to which email will be sent
            username: username of the user for his/her github profile
            token: this token will be his/her personal token. Not required field
        :return: Response for the end user
        """
        serializers = self.serializer_class(data=request.data)

        if serializers.is_valid():
            with transaction.atomic():
                serializers.save()
            data = serializers.data
            create_repos.delay(data['username'])
            return Response(data=data)

        return Response(serializers.errors)
