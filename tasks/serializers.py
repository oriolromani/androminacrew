from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import Task, WorkTime


class TaskSerializer(serializers.ModelSerializer):
    company = serializers.StringRelatedField()

    class Meta:
        model = Task
        fields = ["uid", "name", "start_date", "status", "company", "user"]

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
        try:
            status_choices = {choice[1]: choice[0] for choice in Task.STATUS_CHOICES}
            data["status"] = status_choices[data["status"]]
        except KeyError:
            raise ValidationError("Status field is not valid")
        return super().to_internal_value(data)


class WorkTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkTime
        fields = "__all__"
