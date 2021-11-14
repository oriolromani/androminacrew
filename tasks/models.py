import uuid
from django.db import models
from users.models import Company, CustomUser


class Task(models.Model):
    STATUS_CHOICES = (
        (1, "proposed"),
        (2, "confirmed"),
        (3, "rejected"),
    )
    name = models.CharField(max_length=100)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    start_time = models.DateField()
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="tasks")

    def __str__(self):
        return self.name


class WorkTime(models.Model):
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="times")
