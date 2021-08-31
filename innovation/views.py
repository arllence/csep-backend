from typing import SupportsAbs
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
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.db import IntegrityError, transaction
from app_manager import models as app_manager_models





class InnovationViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,JSONParser)
    queryset = models.Innovation.objects.all().order_by('id')
    serializer_class = serializers.SystemUsersSerializer
    search_fields = ['id', ]

    def get_queryset(self):
        return []

    @action(methods=["GET"], detail=False, url_path="innovation-id", url_name="innovation-id")
    def innovation_id(self, request):
        try:
            innovation = models.Innovation.objects.filter(creator=request.user,status="ONGOING")
            # print(innovation)
            innovation = serializers.InnovationSerializer(innovation, many=True)
            response_info = {
                "innovation_details" : innovation.data,
                "id" : innovation.data[0]['id']
            }
            return Response(response_info, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'details':'Error fetching'},status=status.HTTP_400_BAD_REQUEST)

    
    @action(methods=["GET"], detail=False, url_path="my-innovations", url_name="my-innovations")
    def my_innovations(self, request):
        try:
            innovation = models.Innovation.objects.filter(creator=request.user)
            innovation = serializers.InnovationSerializer(innovation, many=True)
            
            return Response(innovation.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'details':'Error fetching'},status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["POST"], detail=False, url_path="create-innovation",url_name="create-innovation")
    def innovation(self, request):
        authenticated_user = request.user
        payload = request.data
        payload.update({"creator": authenticated_user.id})
        # print(payload)
        serializer = serializers.CreateInnovationSerializer(data=payload, many=False)
        if serializer.is_valid():
            with transaction.atomic():
                term = payload['submission_terms']
                payload = {
                    "submission_terms" : term,
                    "creator" : authenticated_user
                }
                ongoing = models.Innovation.objects.filter(creator=request.user,status="ONGOING").exists()
                if ongoing:
                    return Response({"details": "Kindly Complete The Currently Pending Inovation Before starting  Another "}, status=status.HTTP_400_BAD_REQUEST)
                newinstance = models.Innovation.objects.create(**payload)
                response_info = {
                    "innovation_id" : newinstance.id
                }
                user_util.log_account_activity(
                    authenticated_user, authenticated_user, "Innovation created", "Innovation Creation Executed")
                return Response(response_info, status=status.HTTP_200_OK)
        else:
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["POST"], detail=False, url_path="innovation-details",url_name="innovation-details")
    def innovation_details(self, request):
        authenticated_user = request.user
        payload = request.data
        # payload.update({"creator": authenticated_user.id})
        serializer = serializers.CreateInnovationDetailsSerializer(data=payload, many=False)
        if serializer.is_valid():
            with transaction.atomic():
                innovation = payload['innovation']
                innovation = models.Innovation.objects.get(id=innovation)
                payload['innovation'] = innovation

                industry = payload['industry']
                industry = app_manager_models.Industry.objects.get(id=industry)
                payload['industry'] = industry

                development_stage = payload['development_stage']
                development_stage = app_manager_models.DevelopmentStage.objects.get(id=development_stage)
                payload['development_stage'] = development_stage

                intellectual_property = payload['intellectual_property']
                if intellectual_property == 'None':
                    del payload['intellectual_property']
                else:
                    intellectual_property = app_manager_models.IntellectualProperty.objects.get(id=intellectual_property)
                    payload['intellectual_property'] = intellectual_property
                
                newinstance = models.InnovationDetails.objects.create(**payload)
                
                user_util.log_account_activity(
                    authenticated_user, authenticated_user, "Innovation details created", "Innovation Details Id "  + str(newinstance.id))
                return Response("success", status=status.HTTP_200_OK)
        else:
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["GET"], detail=False, url_path="get-innovation-details", url_name="get-innovation-details")
    def get_innovation_details(self, request):
        innovation_id = request.query_params.get('innovation_id')
        try:
            details = models.InnovationDetails.objects.get(innovation=innovation_id)
            details = serializers.InnovationDetailsSerializer(details, many=False)
            
            return Response(details.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'details':'Error Getting Details'},status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["POST"], detail=False, url_path="innovation-information",url_name="innovation-information")
    def innovation_information(self, request):
        authenticated_user = request.user
        payload = request.data
        print(payload)
        # payload.update({"creator": authenticated_user.id})
        serializer = serializers.InnovationInformationSerializer(data=payload, many=False)
        if serializer.is_valid():
            with transaction.atomic():
                innovation = payload['innovation']
                innovation = models.Innovation.objects.get(id=innovation)
                payload['innovation'] = innovation
                
                newinstance = models.InnovationInformation.objects.create(**payload)
                
                user_util.log_account_activity(
                    authenticated_user, authenticated_user, "Innovation Information created", "Innovation Information Id "  + str(newinstance.id))
                return Response("success", status=status.HTTP_200_OK)
        else:
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["POST"], detail=False, url_path="innovation-additional-details",url_name="innovation-additional-details")
    def innovation_additional_details(self, request):
        authenticated_user = request.user
        payload = request.data
        # print(payload)
        # payload.update({"creator": authenticated_user.id})
        # serializer = serializers.InnovationInformationSerializer(data=payload, many=False)
        # if serializer.is_valid():
        with transaction.atomic():
            innovation = payload['innovation']
            innovation = models.Innovation.objects.get(id=innovation)
            payload['innovation'] = innovation

            support_services = payload['support_service']
            # print(support_services)
            del payload['support_service']

            socialInstance = models.InnovationSocialLinks.objects.create(**payload)

            for service in support_services:
                service = app_manager_models.SupportServices.objects.get(id=int(service))
                to_create = {
                    "innovation" : innovation,
                    "service" : service
                }
                models.InnovationSupportService.objects.create(**to_create)
            
            # innovation.status = "COMPLETED"
            # innovation.save()
            
            user_util.log_account_activity(
                authenticated_user, authenticated_user, "Innovation Social Links created", "Id "  + str(socialInstance.id))
            return Response("success", status=status.HTTP_200_OK)
        # else:
        #     return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["POST"], detail=False, url_path="complete-innovation",url_name="complete-innovation")
    def complete_innovation(self, request):
        authenticated_user = request.user
        payload = request.data

        with transaction.atomic():
            try:
                innovation_id = payload['innovation_id']
            except:
                return Response({'details':'Error, No Innovation Found'},status=status.HTTP_400_BAD_REQUEST)

            innovation = models.Innovation.objects.get(id=innovation_id)
            
            innovation.status = "COMPLETED"
            innovation.save()
            
            user_util.log_account_activity(
                authenticated_user, authenticated_user, "Innovation Completed", "Id "  + str(innovation_id))
            return Response("success", status=status.HTTP_200_OK)


    @action(methods=["GET"], detail=False, url_path="innovation-review", url_name="innovation-review")
    def innovation_review(self, request):
        innovation_id = request.query_params.get('innovation_id')
        try:
            innovation = models.Innovation.objects.get(id=innovation_id)
            innovation = serializers.FullInnovationSerializer(innovation, many=False)
            
            return Response(innovation.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'details':'Error fetching review'},status=status.HTTP_400_BAD_REQUEST)