from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model

from permissions.permissions import CompanyUserPermission
from .models import Task
from .serializers import TaskSerializer, UserTaskSerializer

User = get_user_model()


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
                tasks = [user_task.task for user_task in request.user.user_tasks.all()]
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class CreateUserTask(APIView):
    permission_classes = (IsAuthenticated, CompanyUserPermission)

    def post(self, request):
        """
        Create a UserTask. Only available for company users
        """
        create = True
        data = dict(request.data)
        data["company"] = request.user.company.id
        uid = data.get("uid")
        if uid:
            try:
                task = Task.objects.get(uid=uid)
                create = False
                data.pop("uid")
            except Task.DoesNotExist:
                pass

        serializer = TaskSerializer(data=data)
        if serializer.is_valid():
            if create:
                task = serializer.save()
            if "users" in request.data:
                for user_uid in request.data["users"]:
                    try:
                        user_task_serializer = UserTaskSerializer(
                            data={"task": task.uid, "user": user_uid}
                        )
                        if user_task_serializer.is_valid():
                            user_task_serializer.save()
                        else:
                            Response(
                                user_task_serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST,
                            )
                    except User.DoesNotExist:
                        # TODO: log or communicate a user has not been found
                        pass
            if create:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
