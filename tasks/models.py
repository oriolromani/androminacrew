from django.db import models
from users.models import Company, CustomUser


class Task(models.Model):
    name = models.CharField(max_length=100)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return self.name


class UserTask(models.Model):
    STATUS_CHOICES = (
        (1, "proposed"),
        (2, "confirmed"),
        (3, "rejected"),
    )
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="workers")
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="user_tasks"
    )
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)

    class Meta:
        unique_together = ["task", "user"]

    def __str__(self):
        return " | ".join([self.task.name, self.user.username])


class WorkTime(models.Model):
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
