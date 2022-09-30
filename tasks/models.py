from pyexpat import model
import uuid
from django.utils import timezone
from django.db import models
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from django.dispatch import receiver

from users.models import Company, CustomUser
from utils.utils import send_message_to_user


class Gig(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    venue = models.CharField(max_length=100, null=True, blank=True)
    url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name
    

class Task(models.Model):
    STATUS_CHOICES = (
        (1, "proposed"),
        (2, "confirmed"),
        (3, "rejected"),
    )
    WORK_TYPE_CHOICES = (
        (1, "hours"),
        (2, "full")
    )
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE, null=True, blank=True, related_name="tasks")
    allocation_line_uid = models.UUIDField(null=True, blank=True)
    task_time_type = models.PositiveSmallIntegerField(choices=WORK_TYPE_CHOICES, null=True, blank=True)
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    pay_per_day = models.PositiveIntegerField(null=True, blank=True)
    pay_per_hour = models.PositiveIntegerField(null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="tasks")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_finished = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def time(self):
        """Sum of the work times of the task, returns in hours, minutes, seconds"""
        work_times = self.times.filter(end_time__isnull=False)
        seconds = sum(
            (work_time.end_time - work_time.start_time).seconds
            for work_time in work_times
        )
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return {"hours": hours, "minutes": minutes, "seconds": seconds}

    @property
    def accepted(self):
        """Flag that returns if status is confirmed"""
        return self.status == 2

    @property
    def working_status(self):
        """To inform about the status of the task work times"""
        if not self.is_finished:
            if not self.times.all():
                return "not started"
            if self.times.filter(end_time__isnull=True):
                return "in process"
            else:
                return "stopped"
        else:
            return "finsihed"


class WorkTime(models.Model):
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="times")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task.name} {self.pk}"

    def clean(self, *args, **kwargs):
        """
        Work times in the same taks can't overlap in time.
        A work time can't be created on a task if there
        is a another one which is not finished (a.k.a end_time is null)
        A WorkTime can't have a start or end time after current time
        """
        if self.task_id is None:
            raise ValidationError("Task is mandatory")
        other_work_times = self.task.times.exclude(pk=self.pk)
        if self.end_time:
            overlapping_work_times = other_work_times.filter(
                end_time__gt=self.start_time, start_time__lt=self.end_time
            )
            if overlapping_work_times.exists():
                raise ValidationError("Work times in the same task can't overlap")
        else:
            non_finished_work_times = other_work_times.filter(end_time__isnull=True)
            if non_finished_work_times.exists():
                raise ValidationError("There are not finished work times in the task")
        current_time = timezone.now()
        if self.start_time > current_time:
            raise ValidationError("Start time can't be larger than current time")
        if self.end_time:
            if self.end_time > current_time:
                raise ValidationError("End time can't be larger than current time")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

@receiver(post_save, sender=Task)
def send_message_for_task_create_or_update(sender, instance=None, created=False, **kwargs):
    if created:
        message = f"New task from {instance.company.name}"
    else:
        message = f"Task {instance.name} from {instance.company.name} has changed"
    send_message_to_user(instance.user, message)
