from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

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


class CompanyUsersList(APIView):
    permission_classes = (IsAuthenticated, CompanyUserPermission)

    def get(self, request, *args, **kwargs):
        """
        Get list of invited users
        """
        invitations = Invitation.objects.filter(company=request.user.company)
        serializer = InvitationSerializer(invitations, many=True)
        return Response(serializer.data)
