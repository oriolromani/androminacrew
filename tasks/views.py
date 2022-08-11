from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError
from rest_framework import generics
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from permissions.permissions import CompanyUserPermission
from .models import Task, WorkTime, Gig
from .serializers import TaskSerializer, WorkTimeSerializer, GigSerializer


class GigListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, CompanyUserPermission)
    serializer_class = GigSerializer
    queryset = Gig.objects.all()


class GigDetailView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = GigSerializer
    queryset = Gig.objects.all()
    lookup_field = "uid"


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
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = {
        "date": ["gte", "lte", "exact", "gt", "lt"],
        "status": ["exact"],
    }
    ordering_fields = ["date"]

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


class WorkTimeCreation(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = WorkTimeSerializer
    queryset = WorkTime.objects.all()

    def post(self, request, uid):
        try:
            task = Task.objects.get(uid=uid)
        except Task.DoesNotExist:
            return Response(f"Task {uid} does not exist", status=status.HTTP_400_BAD_REQUEST)
        serializer = WorkTimeSerializer(data=request.data, context={"task": task})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WorkTimeDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = WorkTimeSerializer
    queryset = WorkTime.objects.all()

    def put(self, request, *args, **kwargs):
        try:
            return self.update(request, *args, **kwargs)
        except ValidationError as error:
            return Response(error.messages, status=status.HTTP_400_BAD_REQUEST)
