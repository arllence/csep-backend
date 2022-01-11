from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.conf import settings
from . import models

class SystemUsersSerializer(serializers.Serializer):
    UserId = serializers.CharField()
    email = serializers.CharField()
    firstname = serializers.CharField()
    lastname = serializers.CharField()


class SupportServicesSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    service = serializers.CharField()
    description = serializers.CharField()


class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Industry
        fields = '__all__'

class DevelopmentStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DevelopmentStage
        fields = '__all__'

class IntellectualPropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IntellectualProperty
        fields = '__all__'


class SkillsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Skills
        fields = '__all__'


class EmploymentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EmploymentStatus
        fields = '__all__'


class IntellectualPropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IntellectualProperty
        fields = '__all__'
