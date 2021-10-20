from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from permissions.permissions import CompanyUserPermission

from .models import CustomUser, Invitation
from .serializers import UserSerializer, InvitationSerializer


class UsersList(APIView):
    permission_classes = (IsAuthenticated, CompanyUserPermission)

    def get(self, request, *args, **kwargs):
        """
        Get list of all users
        """
        users = CustomUser.objects.filter(is_company=False)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


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


class CompanyUsersList(APIView):
    permission_classes = (IsAuthenticated, CompanyUserPermission)

    def get(self, request, *args, **kwargs):
        """
        Get list of invited users
        """
        invitations = Invitation.objects.filter(company=request.user.company)
        serializer = InvitationSerializer(invitations, many=True)
        return Response(serializer.data)


class CustomObtainToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "username": user.username, "pk": user.pk})
