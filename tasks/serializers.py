from rest_framework import serializers

from .models import Task, WorkTime


class TaskSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField("_status")
    company = serializers.StringRelatedField()

    @staticmethod
    def _status(obj):
        """
        Return status name instead of id
        """
        status_choices = {choice[0]: choice[1] for choice in Task.STATUS_CHOICES}
        return status_choices[obj.status]

    class Meta:
        model = Task
        fields = ["uid", "name", "start_date", "status", "company", "user"]

    def create(self, validated_data):
        company = self.context.get("company")
        validated_data["company"] = company
        task = Task.objects.create(**validated_data)
        return task


class WorkTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkTime
        fields = "__all__"
