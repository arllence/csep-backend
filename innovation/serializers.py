from app_manager.models import Industry
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.conf import settings
from . import models
from user_manager.serializers import UsersSerializer
from app_manager import serializers as app_manager_serializers
from app_manager import models as app_manager_models

import innovation



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



class InnovationDetailsSerializer(serializers.ModelSerializer):
    # innovation = InnovationSerializer()
    industry = serializers.SerializerMethodField('get_industry')
    # development_stage = app_manager_serializers.DevelopmentStageSerializer()
    # intellectual_property = app_manager_serializers.IntellectualPropertySerializer()
    class Meta:
        model = models.InnovationDetails
        fields = '__all__'

    def get_industry(self, obj):
        print(obj.__dict__)
        industry = app_manager_models.Industry.objects.get(id=obj.industry_id)
        print("industry: ", industry)
        serializer = app_manager_serializers.IndustrySerializer(industry, many=False)
        return serializer.data

class InnovationSerializer(serializers.ModelSerializer):
    creator = UsersSerializer()
    details = serializers.SerializerMethodField('get_details')
    class Meta:
        model = models.Innovation
        fields = '__all__'
    
    def get_details(self, obj):
        try:
            details = models.InnovationDetails.objects.get(innovation=obj.id)
            serializer = InnovationDetailsSerializer(details, many=False)
            return serializer.data
        except:
            return []

class CreateInnovationSerializer(serializers.Serializer):
    creator = serializers.UUIDField()
    submission_terms = serializers.BooleanField()

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
    # innovation = InnovationSerializer()    
    class Meta:
        model = models.InnovationSocialLinks
        fields = '__all__'


class InnovationSupportServiceSerializer(serializers.ModelSerializer):
    # innovation = InnovationSerializer()
    service = SupportServicesSerializer()
    
    class Meta:
        model = models.InnovationSupportService
        fields = '__all__'

class FullInnovationSerializer(serializers.ModelSerializer):
    creator = UsersSerializer()
    details = serializers.SerializerMethodField(read_only=True)
    information = serializers.SerializerMethodField(read_only=True)
    support_services = serializers.SerializerMethodField(read_only=True)
    social_links = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = models.Innovation
        fields = '__all__'


    def get_details(self, obj):
        details = models.InnovationDetails.objects.filter(innovation=obj)
        serializer = InnovationDetailsSerializer(details, many=True)
        return serializer.data

    def get_information(self, obj):
        information = models.InnovationInformation.objects.filter(innovation=obj)
        serializer = InnovationInformationSerializer(information, many=True)
        return serializer.data

    def get_support_services(self, obj):
        support_services = models.InnovationSupportService.objects.filter(innovation=obj)
        serializer = InnovationSupportServiceSerializer(support_services, many=True)
        return serializer.data

    def get_social_links(self, obj):
        social_links = models.InnovationSocialLinks.objects.filter(innovation=obj)
        serializer = InnovationSocialLinksSerializer(social_links, many=True)
        return serializer.data