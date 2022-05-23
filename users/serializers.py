from rest_framework import serializers

from .models import CustomUser, Company


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "first_name", "last_name", "email", "uid"]

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"
