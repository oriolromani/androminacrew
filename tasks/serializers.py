from rest_framework import serializers

from .models import Task, UserTask, WorkTime


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


class UserTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTask
        fields = "__all__"


class WorkTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkTime
        fields = "__all__"
