import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token


def get_default_uid():
    return uuid.uuid4().hex[:6].upper()


class CustomUser(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField("email_address")
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_company = models.BooleanField(default=False)
    uid = models.CharField(
        primary_key=True,
        default=get_default_uid,
        max_length=6,
        unique=True,
    )


class Company(models.Model):
    name = models.CharField(max_length=100)
    user = models.OneToOneField(CustomUser, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return self.name


class Invitation(models.Model):
    STATUS_CHOICES = (
        (1, "proposed"),
        (2, "confirmed"),
        (3, "rejected"),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)

    class Meta:
        unique_together = ["company", "user"]


@receiver(post_save, sender=CustomUser)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=Company)
def fill_user_is_company(sender, instance, **kwargs):
    instance.user.is_company = hasattr(instance.user, "company")
    instance.user.save()
