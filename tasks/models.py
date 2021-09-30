from django.db import models
from django.contrib.auth.models import User

from users.models import Company


class Task(models.Model):
    name = models.CharField(max_length=100)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


class UserTask(models.Model):
    STATUS_CHOICES = (
        (1, "proposed"),
        (2, "confirmed"),
        (3, "rejected"),
    )
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="workers")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_tasks")
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES)

    class Meta:
        unique_together = ["task", "user"]


class WorkTime(models.Model):
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField()
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
