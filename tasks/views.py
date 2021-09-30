from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from permissions.permissions import CompanyUserPermission
from .models import Task
from .serializers import TaskSerializer, UserTaskSerializer


class TaskList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """
        Retrieve the tasks according to the user.
        - admin user: all tasks
        - company user: the taks of the company
        - user: the tasks proposed to the user

        """
        if request.user.is_staff:
            tasks = Task.objects.all()
        else:
            try:
                company = request.user.company
                tasks = Task.objects.filter(company=company)
            except AttributeError:
                tasks = request.user.user_tasks.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Create a Task only if user is a company
        """
        if hasattr(request.user, "company"):
            serializer = TaskSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(company=request.user.company)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response("User is not a company user", status=status.HTTP_403_FORBIDDEN)


class CreateUserTask(APIView):
    permission_classes = (IsAuthenticated, CompanyUserPermission)

    def post(self, request, *args, **kwargs):
        """
        Create a UserTask. Only available for company users
        """
        serializer = UserTaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
