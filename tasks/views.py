from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from permissions.permissions import CompanyUserPermission
from .models import Task
from .serializers import TaskSerializer


class BaseTaskView(generics.GenericAPIView):
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            tasks = Task.objects.all()
        else:
            if user.is_company:
                tasks = Task.objects.filter(company=user.company)
            else:
                tasks = user.tasks.all()
        return tasks


class TaskList(BaseTaskView, generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, CompanyUserPermission)
    serializer_class = TaskSerializer


class TaskDetail(BaseTaskView, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    lookup_field = "uid"
