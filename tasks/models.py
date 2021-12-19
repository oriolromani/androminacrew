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
    start_date = models.DateField()
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="tasks")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def time(self):
        """Sum of the work times of the task"""
        time = 0
        for work_time in self.times.filter(end_time__isnull=False):
            time += int(
                (work_time.end_time - work_time.start_time).total_seconds() // 60
            )
        return time


class WorkTime(models.Model):
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="times")

    def __str__(self):
        return f"{self.task.name} {self.pk}"
