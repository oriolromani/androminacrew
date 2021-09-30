from rest_framework import serializers

from .models import Task, UserTask, WorkTime


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["name", "start_time", "end_time"]


class UserTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTask
        fields = ["task", "user", "status"]

    def to_internal_value(self, data):
        print()
        return super().to_internal_value(data)


class WorkTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkTime
        fields = "__all__"
