from app_manager.models import Industry
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.conf import settings
from . import models
from user_manager.serializers import UsersSerializer
from app_manager import serializers as app_manager_serializers
from app_manager import models as app_manager_models



# from user_manager import models as models

class SystemUsersSerializer(serializers.Serializer):
    UserId = serializers.CharField()
    email = serializers.CharField()
    firstname = serializers.CharField()
    lastname = serializers.CharField()


class SupportServicesSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    service = serializers.CharField()
    description = serializers.CharField()

    class Meta:
        model = app_manager_models.SupportServices
        fields = '__all__'

class InnovationSerializer(serializers.ModelSerializer):
    creator = UsersSerializer()
    class Meta:
        model = models.Innovation
        fields = '__all__'

class InnovationDetailsSerializer(serializers.ModelSerializer):
    innovation = InnovationSerializer()
    Industry = app_manager_serializers.IndustrySerializer()
    development_stage = app_manager_serializers.DevelopmentStageSerializer()
    intellectual_property = app_manager_serializers.IntellectualPropertySerializer()
    class Meta:
        model = models.InnovationDetails
        fields = '__all__'

class CreateInnovationDetailsSerializer(serializers.Serializer):
    innovation = serializers.CharField()
    innovation_name = serializers.CharField()
    area_of_focus = serializers.CharField()
    development_stage = serializers.CharField()
    hub_affiliation = serializers.CharField()
    intellectual_property = serializers.CharField()
    industry = serializers.CharField()


class InnovationInformationSerializer(serializers.ModelSerializer):
    # innovation = InnovationSerializer()
    class Meta:
        model = models.InnovationInformation
        fields = '__all__'


class InnovationSocialLinksSerializer(serializers.ModelSerializer):
    innovation = InnovationSerializer()    
    class Meta:
        model = models.InnovationSocialLinks
        fields = '__all__'


class InnovationSupportServiceSerializer(serializers.ModelSerializer):
    innovation = InnovationSerializer()
    service = SupportServicesSerializer()
    
    class Meta:
        model = models.InnovationSupportService
        fields = '__all__'