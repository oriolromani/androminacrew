import copy
from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import Gig, Task, WorkTime
from users.serializers import CompanySerializer


class WorkTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkTime
        fields = ["id", "start_time", "end_time"]

    def create(self, validated_data):
        task = self.context.get("task")
        validated_data["task"] = task
        try:
            work_time = WorkTime.objects.create(**validated_data)
        except ValidationError as validation_error:
            raise serializers.ValidationError(validation_error.args[0])
        return work_time

class GigSerializer(serializers.ModelSerializer):

    class Meta:
        model = Gig
        fields = ["uid", "name", "venue", "url", "tasks"]

    def get_tasks(self, instance):
        return TaskSerializer(instance.tasks.all())
    
    
class TaskSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    gig = GigSerializer(read_only=True)
    times = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "uid",
            "name",
            "company",
            "gig",
            "allocation_line_uid",
            "task_time_type",
            "date",
            "start_time",
            "end_time",
            "status",
            "pay_per_day",
            "pay_per_hour",
            "category",
            "user",
            "created_at",
            "updated_at",
            "times",
        ]

    def get_times(self, instance):
        times = instance.times.order_by("-start_time")
        return WorkTimeSerializer(times, many=True).data

    def create(self, validated_data):
        company = self.context.get("company")
        validated_data["company"] = company
        task = Task.objects.create(**validated_data)
        return task

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["status"] = instance.get_status_display()
        return data

    def to_internal_value(self, data):
        modified_data = copy.deepcopy(data)
        status_choices = {choice[1]: str(choice[0]) for choice in Task.STATUS_CHOICES}
        if "status" in modified_data:
            if modified_data["status"] not in status_choices.values():
                modified_data["status"] = status_choices.get(modified_data["status"])
        return super().to_internal_value(modified_data)
