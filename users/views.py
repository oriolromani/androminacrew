from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from .models import CustomUser
from .serializers import UserSerializer


class UsersList(generics.ListAPIView):
    """
    List and create Users
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_queryset(self):
        return CustomUser.objects.filter(is_company=False)


class UserDetail(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """
        Get detail of the user
        """
        serializer = UserSerializer(self.request.user)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        """
        Update user fields
        """
        serializer = UserSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)


class CustomObtainToken(ObtainAuthToken):
    """
    Obtain user
    """

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "username": user.username, "pk": user.pk})
