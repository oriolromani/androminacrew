from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

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
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        "start_date": ["gte", "lte", "exact", "gt", "lt"],
        "status": ["exact"],
    }

    def post(self, request, *args, **kwargs):
        serializer = TaskSerializer(
            data=request.data, context={"company": self.request.user.company}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetail(BaseTaskView, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    lookup_field = "uid"
