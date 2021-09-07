from rest_framework.views import APIView
from . import models
from . import serializers 
from django.contrib.auth import authenticate
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import Permission
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets, status
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta, date
from user_manager.utils import user_util
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.db import IntegrityError, transaction



class AdminManagementViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,JSONParser)
    queryset = models.SupportServices.objects.all().order_by('id')
    serializer_class = serializers.SystemUsersSerializer
    search_fields = ['id', ]

    def get_queryset(self):
        return []

    @action(methods=["GET"], detail=False, url_path="support-services", url_name="support-services")
    def support_services(self, request):
        try:
            services = models.SupportServices.objects.filter(status=True).order_by('service')
            services = serializers.SupportServicesSerializer(services, many=True)
            return Response(services.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'details':'Error fetching support services'},status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["GET"], detail=False, url_path="industries", url_name="industries")
    def industry(self, request):
        try:
            industry = models.Industry.objects.filter(status=True).order_by('name')
            industry = serializers.IndustrySerializer(industry, many=True)
            return Response(industry.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'details':'Error fetching industries'},status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["GET"], detail=False, url_path="development-stages", url_name="development-stages")
    def development_stage(self, request):
        try:
            development_stage = models.DevelopmentStage.objects.filter(status=True).order_by('name')
            development_stage = serializers.DevelopmentStageSerializer(development_stage, many=True)
            return Response(development_stage.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'details':'Error fetching development stages'},status=status.HTTP_400_BAD_REQUEST)

    
    @action(methods=["GET"], detail=False, url_path="intellectual-properties", url_name="intellectual-properties")
    def intellectual_property(self, request):
        try:
            intellectual_property = models.IntellectualProperty.objects.filter(status=True).order_by('name')
            intellectual_property = serializers.IntellectualPropertySerializer(intellectual_property, many=True)
            return Response(intellectual_property.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'details':'Error fetching intellectual properties'},status=status.HTTP_400_BAD_REQUEST)

    
    @action(methods=["GET"], detail=False, url_path="hubs", url_name="hubs")
    def hubs(self, request):
        try:
            hubs = models.Hubs.objects.filter(status=True).order_by('name')
            hubs = serializers.IntellectualPropertySerializer(hubs, many=True)
            return Response(hubs.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'details':'Error fetching intellectual properties'},status=status.HTTP_400_BAD_REQUEST)



    @action(methods=["GET"], detail=False, url_path="innovation-skills", url_name="innovation-skills")
    def innovation_skills(self, request):
        try:
            skills = models.Skills.objects.filter(status=True)
            skills = serializers.SkillsSerializer(skills, many=True)
            return Response(skills.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'details':'Error Fetching Skills'},status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["GET"], detail=False, url_path="employment-status", url_name="employment-status")
    def employment_status(self, request):
        try:
            employment_status = models.EmploymentStatus.objects.filter(status=True)
            employment_status = serializers.EmploymentStatusSerializer(employment_status, many=True)
            return Response(employment_status.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'details':'Error Fetching Skills'},status=status.HTTP_400_BAD_REQUEST)