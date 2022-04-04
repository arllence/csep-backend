import json
import logging
from typing import SupportsAbs
from user_manager.models import Document
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
from string import Template
from django.db.models import Q

import innovation

# create and configure logger
# loggername = str(date.today())
# logging.basicConfig(
#     filename=f"/opt/logs/innovation/{loggername}",
#     format='%(asctim)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s',
#     filemode='a'
# )
# # new logger object
# logger = logging.getLogger()

# # setting threshold of logger
# logger.setLevel(logging.DEBUG)

# Get an instance of a logger
logger = logging.getLogger(__name__)


def read_template(filename):
    """
    Returns a template object comprising of the contents of the
    file specified by the filename ie messageto client
    """
    with open("email_template/"+filename, 'r', encoding='utf8') as template_file:
        template_file_content = template_file.read()
        return Template(template_file_content)


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
            innovation = models.Innovation.objects.filter(creator=request.user,status="ONGOING").order_by('-date_created')
            # print(innovation)
            if innovation:
                innovation = serializers.InnovationSerializer(innovation, many=True)
                response_info = {
                    "innovation_details" : innovation.data,
                    "id" : innovation.data[0]['id']
                }
                return Response(response_info, status=status.HTTP_200_OK)
            else:
                return Response({}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response({'details':'Error Fetching Innovation'},status=status.HTTP_400_BAD_REQUEST)

    
    @action(methods=["GET"], detail=False, url_path="innovations", url_name="innovations")
    def innovations(self, request):
        user = request.user
        try:
            roles = user_util.fetchusergroups(user.id)
            if "LEAD_INNOVATION_MANAGER" in roles:
                innovation = models.Innovation.objects.exclude(status__in=('DROPED','DROPPED','ONGOING')).order_by('-date_created')
                # print(innovation)
                if innovation:
                    innovations = serializers.FullInnovationSerializer(innovation, many=True ,context={"user_id":request.user.id}).data

                    return Response(innovations, status=status.HTTP_200_OK)
                else:
                    return Response([], status=status.HTTP_200_OK)
            else:
                return Response([], status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response({'details':'Error Fetching Innovations'},status=status.HTTP_400_BAD_REQUEST)

    
    @action(methods=["GET"], detail=False, url_path="innovation", url_name="innovation")
    def fetch_innovation(self, request):
        innovation_id = request.query_params.get('innovation_id')
        if not innovation_id:
            return Response({'details':'Innovation Id Required'},status=status.HTTP_400_BAD_REQUEST)
        try:
            innovation = models.Innovation.objects.get(id=innovation_id)
            # print(innovation)
            if innovation:
                innovations = serializers.FullInnovationSerializer(innovation, many=False,context={"user_id":request.user.id}).data
                return Response(innovations, status=status.HTTP_200_OK)
            else:
                return Response([], status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response({'details':'Error Fetching Innovation'},status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["GET"], detail=False, url_path="filter-innovations", url_name="filter-innovations")
    def filter_innovations(self, request):
        user = request.user
        status_value = request.query_params.get('status')
        stage = request.query_params.get('stage')
        if not status_value:
            return Response({'details':'Status Required'},status=status.HTTP_400_BAD_REQUEST)
        
        is_chief_evaluator = False
        is_lead_innovation_manager = False
        is_lead = False
        role = None

        roles = user_util.fetchusergroups(user.id)

        for item in roles:
            if 'LEAD' not in item:
                if 'CHIEF' not in item:
                    role = item
                else:
                    is_chief_evaluator = True
                    role = 'CHIEF_EVALUATOR'
            else:
                is_lead = True
                if item == 'LEAD_INNOVATION_MANAGER':
                    is_lead_innovation_manager = True

        try:    
            if is_lead_innovation_manager:
                if status_value == 'ALL' and stage == 'ALL':
                    innovations = models.Innovation.objects.all().order_by('-date_created')
                elif status_value == 'ALL' and stage != 'ALL':
                    innovations = models.Innovation.objects.filter(stage=stage).order_by('-date_created')
                elif status_value != 'ALL' and stage == 'ALL':
                    innovations = models.Innovation.objects.filter(status=status_value).order_by('-date_created')
                elif status_value != 'ALL' and stage != 'ALL':
                    innovations = models.Innovation.objects.filter(status=status_value,stage=stage).order_by('-date_created')

                if innovations:
                    innovations = serializers.FullInnovationSerializer(innovations, many=True,context={"user_id":request.user.id}).data
                    return Response(innovations, status=status.HTTP_200_OK)
                else:
                    return Response([], status=status.HTTP_200_OK)
            else:
                innovations = models.GroupMember.objects.filter(member=user, group__role=role).order_by('-date_created')
                innovation_pks = []
                for innovation in innovations:
                    innovation_pks.append(innovation.group.innovation.id)
                   
                # innovation = models.Innovation.objects.filter(pk__in=innovation_pks, status=status).order_by('-date_created')

                if status_value == 'ALL' and stage == 'ALL':
                    innovation = models.Innovation.objects.filter(pk__in=innovation_pks).order_by('-date_created')
                elif status_value == 'ALL' and stage != 'ALL':
                    innovation = models.Innovation.objects.filter(pk__in=innovation_pks, stage=stage).order_by('-date_created')
                elif status_value != 'ALL' and stage == 'ALL':
                    innovation = models.Innovation.objects.filter(pk__in=innovation_pks, status=status_value).order_by('-date_created')
                elif status_value != 'ALL' and stage != 'ALL':
                    innovation = models.Innovation.objects.filter(pk__in=innovation_pks, status=status_value, stage=stage).order_by('-date_created')
                
                if innovation:
                    innovations = serializers.FullInnovationSerializer(innovation, many=True, context={"user_id":request.user.id}).data
                    return Response(innovations, status=status.HTTP_200_OK)

            return Response([], status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(e)
            return Response({'details':'Error Fetching Analytics'},status=status.HTTP_400_BAD_REQUEST)

    
    @action(methods=["GET"], detail=False, url_path="assigned-innovations", url_name="assigned-innovations")
    def assigned_innovations(self, request):
        user = request.user
        try:
            innovation_pks = []

            is_chief_evaluator = False
            is_lead = False

            role = None
            roles = user_util.fetchusergroups(user.id)
            for item in roles:
                if 'LEAD' not in item:
                    if 'CHIEF' not in item:
                        role = item
                    else:
                        is_chief_evaluator = True
                        role = 'CHIEF_EVALUATOR'
                else:
                    is_lead = True


            innovations = models.GroupMember.objects.filter(member=user, group__role=role).order_by('-date_created')
            # innovations = models.GroupMember.objects.filter(member=user)
            for innovation in innovations:
                # innovation_pks.append(innovation.group.innovation.id)
                stage = innovation.group.innovation.stage
                check = True
                if role == 'JUNIOR_OFFICER':
                    stages = ['I','II']
                    check = models.InnovationReview.objects.filter(innovation=innovation.group.innovation.id,reviewer=user)
                    if is_lead:
                        if stage in stages:
                            check_is_final = models.InnovationReview.objects.filter(innovation=innovation.group.innovation.id,is_final=True).exists()
                            if not check_is_final:
                                innovation_pks.append(innovation.group.innovation.id)
                        else:
                            is_lead = False
                elif role == 'CHIEF_EVALUATOR':
                    check = models.FinalEvaluatorsComment.objects.filter(innovation=innovation.group.innovation.id,stage=innovation.group.innovation.stage).exists()
                else:
                    check = models.Evaluation.objects.filter(innovation=innovation.group.innovation.id,evaluator=user).exists()
                    if is_lead:
                        if role == 'INTERNAL_EVALUATOR':
                            check_is_final = models.FinalEvaluatorsComment.objects.filter(innovation=innovation.group.innovation.id,stage='VI').exists()
                        else:
                            check_is_final = models.FinalEvaluatorsComment.objects.filter(innovation=innovation.group.innovation.id,stage=innovation.group.innovation.stage).exists()

                        if not check_is_final:
                            innovation_pks.append(innovation.group.innovation.id)

                if not check:
                    innovation_pks.append(innovation.group.innovation.id)

                # if is_chief_evaluator:
                #     innovation_pks.append(innovation.group.innovation.id)

            innovation = models.Innovation.objects.filter(pk__in=innovation_pks).exclude(status__in=('DROPED','DROPPED','ONGOING')).order_by('-date_created')
            
            if innovation:
                innovations = serializers.FullInnovationSerializer(innovation, many=True, context={"user_id":request.user.id}).data

                return Response(innovations, status=status.HTTP_200_OK)
            else:
                return Response([], status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response({'details':'Error Fetching Innovations'},status=status.HTTP_400_BAD_REQUEST)

    
    @action(methods=["GET"], detail=False, url_path="my-innovations", url_name="my-innovations")
    def my_innovations(self, request):
        try:
            innovation = models.Innovation.objects.filter(creator=request.user).order_by('-date_created')
            innovation = serializers.FullInnovationSerializer(innovation, many=True)            
            return Response(innovation.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response({'details':'Error Fetching Your Innovations'},status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["GET"], detail=False, url_path="pending-final-review", url_name="pending-final-review")
    def pending_final_review(self, request):
        try:
            innovations = []
            innovation = models.PendingFinalReport.objects.filter(status=True).order_by('-date_created')
            for i in innovation:
                innovations.append(i.innovation)
            innovation = serializers.FullInnovationSerializer(innovations, many=True)            
            return Response(innovation.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response({'details':'Error Fetching Your Innovations'},status=status.HTTP_400_BAD_REQUEST)
            

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
                    "creator" : authenticated_user,
                    "edit" : True
                }
                ongoing = models.Innovation.objects.filter(creator=request.user,status="ONGOING").exists()
                if ongoing:
                    return Response({"status":"ongoing"}, status=status.HTTP_200_OK)
                newinstance = models.Innovation.objects.create(**payload)
                response_info = {
                    "innovation_id" : newinstance.id,
                    "status":"created"
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
        for key in payload:
            if not payload[key]:
                payload[key] = None

        serializer = serializers.CreateInnovationDetailsSerializer(data=payload, many=False)
        if serializer.is_valid():
            with transaction.atomic():
                innovation = payload['innovation']
                innovation = models.Innovation.objects.get(id=innovation)
                payload['innovation'] = innovation

                industry = payload['industry']
                try:
                    industry = app_manager_models.Industry.objects.get(id=industry)
                    payload['industry'] = industry
                except Exception as e:
                    logger.error(e)
                    return Response({"details": "Select Industry from the list!"}, status=status.HTTP_400_BAD_REQUEST)

                development_stage = payload['development_stage']
                development_stage = app_manager_models.DevelopmentStage.objects.get(id=development_stage)
                payload['development_stage'] = development_stage

                intellectual_property = payload['intellectual_property']
                if intellectual_property == 'None':
                    del payload['intellectual_property']
                else:
                    intellectual_property = app_manager_models.IntellectualProperty.objects.get(id=intellectual_property)
                    payload['intellectual_property'] = intellectual_property

                for key in payload:
                    if not payload[key]:
                        payload[key] = None

                if payload['awards']:
                    for award in payload['awards']:
                        data = {
                            "innovation" : innovation,
                            "name" : award['value'].upper()
                        }
                        models.Awards.objects.create(**data)
                del payload['awards']


                if payload['recognitions']:
                    for recognition in payload['recognitions']:
                        data = {
                            "innovation" : innovation,
                            "name" : recognition['value'].upper()
                        }
                        models.Recognitions.objects.create(**data)
                del payload['recognitions']


                if payload['accreditation_bodies']:
                    for accreditation in payload['accreditation_bodies']:
                        data = {
                            "innovation" : innovation,
                            "name" : accreditation['value'].upper()
                        }
                        models.AccreditationBody.objects.create(**data)
                del payload['accreditation_bodies']

                # print(payload)
                newinstance = models.InnovationDetails.objects.create(**payload)
                
                user_util.log_account_activity(
                    authenticated_user, authenticated_user, "Innovation details created", "Innovation Details Id "  + str(newinstance.id))
                return Response("success", status=status.HTTP_200_OK)
        else:
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["POST"], detail=False, url_path="update-innovation-details",url_name="update-innovation-details")
    def update_innovation_details(self, request):
        authenticated_user = request.user
        payload = request.data
        # payload.update({"creator": authenticated_user.id})
        for key in payload:
            if not payload[key]:
                payload[key] = None
        serializer = serializers.CreateInnovationDetailsSerializer(data=payload, many=False)
        if serializer.is_valid():
            with transaction.atomic():
                # print(payload)
                try:
                    innovation = payload['innovation']
                    innovation = models.Innovation.objects.get(id=innovation)
                except Exception as e:
                    logger.error(e)
                    return Response({'details': 'Missing Innovation Id'},status=status.HTTP_400_BAD_REQUEST )

                try:
                    details_id = payload['details_id']
                    details_instance = models.InnovationDetails.objects.get(id=details_id)
                except Exception as e:
                    logger.error(e)
                    return Response({'details': 'Missing Details Id'},status=status.HTTP_400_BAD_REQUEST )

                try:
                    industry = payload['industry']
                    industry = app_manager_models.Industry.objects.get(id=industry)
                    details_instance.industry = industry
                except Exception as e:
                    logger.error(e)

                try:
                    development_stage = payload['development_stage']
                    development_stage = app_manager_models.DevelopmentStage.objects.get(id=development_stage)
                    details_instance.development_stage = development_stage
                except Exception as e:
                    logger.error(e)

                intellectual_property = payload['intellectual_property']
                if intellectual_property != 'None' or intellectual_property != 'None of the above':
                    try:
                        intellectual_property = app_manager_models.IntellectualProperty.objects.get(id=intellectual_property)
                        details_instance.intellectual_property = intellectual_property
                    except Exception as e:
                        logger.error(e)
                
                # attended = ['intellectual_property', 'development_stage', 'industry','accreditation_bodies','awards','recognitions']

                if payload['awards']:
                    saved_data = []
                    current_data = []
                    saved = models.Awards.objects.filter(innovation=innovation)
                    for data in saved: saved_data.append(data.name)
                    for award in payload['awards']:
                        try:
                            name = award['value'].upper()
                        except Exception as e:
                            logger.error(e)
                            name = award.upper()
                        current_data.append(name)
                        if not models.Awards.objects.filter(name=name,innovation=innovation).exists():
                            data = {
                                "innovation" : innovation,
                                "name" : name
                            }
                            models.Awards.objects.create(**data)
                    for sdata in saved_data:
                        if sdata not in current_data:
                            models.Awards.objects.filter(name=sdata,innovation=innovation).delete()
                else:
                    models.Awards.objects.filter(innovation=innovation).delete()
                


                if payload['recognitions']:
                    saved_data = []
                    current_data = []
                    saved = models.Recognitions.objects.filter(innovation=innovation)
                    for data in saved: saved_data.append(data.name)
                    for recognition in payload['recognitions']:
                        try:
                            name = recognition['value'].upper()
                        except Exception as e:
                            name = recognition.upper()
                        current_data.append(name)
                        if not models.Recognitions.objects.filter(name=name,innovation=innovation).exists():
                            data = {
                                "innovation" : innovation,
                                "name" : name
                            }
                            models.Recognitions.objects.create(**data)
                    for sdata in saved_data:
                        if sdata not in current_data:
                            models.Recognitions.objects.filter(name=sdata,innovation=innovation).delete()
                else:
                    models.Recognitions.objects.filter(innovation=innovation).delete()

                if payload['accreditation_bodies']:
                    saved_data = []
                    current_data = []
                    saved = models.AccreditationBody.objects.filter(innovation=innovation)
                    for data in saved: saved_data.append(data.name)
                    for accreditation in payload['accreditation_bodies']:
                        try:
                            name = accreditation['value'].upper()
                        except Exception as e:
                            name = accreditation.upper()
                        current_data.append(name)
                        if not models.AccreditationBody.objects.filter(name=name,innovation=innovation).exists():
                            data = {
                                "innovation" : innovation,
                                "name" : name
                            }
                            models.AccreditationBody.objects.create(**data)
                    for sdata in saved_data:
                        if sdata not in current_data:
                            models.AccreditationBody.objects.filter(name=sdata,innovation=innovation).delete()
                else:
                    models.AccreditationBody.objects.filter(innovation=innovation).delete()


                
                details_instance.innovation_name = payload['innovation_name']
                details_instance.other_industry = payload['other_industry']
                details_instance.area_of_focus = payload['area_of_focus']
                details_instance.is_pitched_before = payload['is_pitched_before']
                details_instance.has_won_awards = payload['has_won_awards']
                details_instance.require_accreditation = payload['require_accreditation']
                details_instance.hub_affiliation = payload['hub_affiliation']
                details_instance.hub_name = payload['hub_name']
                details_instance.other_hub_name = payload['other_hub_name']
                details_instance.save()
                
                user_util.log_account_activity(
                    authenticated_user, authenticated_user, "Innovation details Updated", "Innovation Details Id "  + str(details_instance.id))
                return Response("success", status=status.HTTP_200_OK)
        else:
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["GET"], detail=False, url_path="get-innovation-details", url_name="get-innovation-details")
    def get_innovation_details(self, request):
        innovation_id = request.query_params.get('innovation_id')
        if not innovation_id:
            return Response({'details':'Innovation Id Required'},status=status.HTTP_400_BAD_REQUEST)
        try:
            details = models.InnovationDetails.objects.get(innovation=innovation_id)
            # print("details", details)
            details = serializers.InnovationDetailsSerializer(details, many=False)
            
            return Response(details.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response({'status': False}, status=status.HTTP_200_OK)
            # return Response({'details':'Error Getting Details'},status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["POST"], detail=False, url_path="innovation-information",url_name="innovation-information")
    def innovation_information(self, request):
        authenticated_user = request.user
        payload = request.data
        # print(payload)
        # payload.update({"creator": authenticated_user.id})
        serializer = serializers.InnovationInformationSerializer(data=payload, many=False)
        if serializer.is_valid():
            with transaction.atomic():
                innovation_id = payload['innovation']
                innovation_exists = models.InnovationInformation.objects.filter(innovation=innovation_id)
                innovation = models.Innovation.objects.get(id=innovation_id)
                payload['innovation'] = innovation

                if innovation_exists:
                    instance = innovation_exists.first()
                    instance.innovation_brief = payload['innovation_brief']
                    instance.problem_statement = payload['problem_statement']
                    instance.background_research = payload['background_research']
                    instance.target_customers = payload['target_customers']
                    instance.value_proposition = payload['value_proposition']
                    instance.solution = payload['solution']
                    instance.how_it_works = payload['how_it_works']
                    instance.impact = payload['impact']
                    instance.competitors = payload['competitors']
                    instance.competitive_advantage = payload['competitive_advantage']
                    instance.save()
                    instance_status = "Innovation Information Updated"
                    instance_id = instance.id
                else:
                    newinstance = models.InnovationInformation.objects.create(**payload)
                    instance_status = "Innovation Information Created"
                    instance_id = newinstance.id
                
                
                user_util.log_account_activity(
                    authenticated_user, authenticated_user, instance_status, "Innovation Information Id "  + str(instance_id))
                return Response("success", status=status.HTTP_200_OK)
        else:
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    
    @action(methods=["GET"], detail=False, url_path="get-innovation-information", url_name="get-innovation-information")
    def get_innovation_information(self, request):
        innovation_id = request.query_params.get('innovation_id')
        if not innovation_id:
            return Response({'details':'Innovation Id Required'},status=status.HTTP_400_BAD_REQUEST)
        try:
            information = models.InnovationInformation.objects.get(innovation=innovation_id)
            information = serializers.InnovationInformationSerializer(information, many=False)
            
            return Response(information.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response({'status': False}, status=status.HTTP_200_OK)


    @action(methods=["POST"], detail=False, url_path="innovation-additional-details",url_name="innovation-additional-details")
    def innovation_additional_details(self, request):
        authenticated_user = request.user
        payload = request.data
        # print(payload)
        with transaction.atomic():
            innovation_id = payload['innovation']
            innovation = models.Innovation.objects.get(id=innovation_id)
            payload['innovation'] = innovation
            other_support = payload['other_support']
            # print("innovation: ",innovation.__dict__)

            support_services = []
                
            try:
                support_services = payload['support_service']
            except Exception as e:
                logger.error(e)

            del payload['support_service']
            del payload['other_support']

            try:
                otherSupport = models.OtherInnovationSupportService.objects.filter(innovation=innovation_id)
                if otherSupport:
                    otherSupport = otherSupport.first()
                    otherSupport.service = other_support
                    otherSupport.save()
                else:
                    models.OtherInnovationSupportService.objects.create(innovation=innovation, service=other_support)
            except Exception as e:
                logger.error(e)


            links_exists =  models.InnovationSocialLinks.objects.filter(innovation=innovation_id).exists()
            # print("links_exists: ", links_exists)
            if links_exists:
                instance = models.InnovationSocialLinks.objects.get(innovation=innovation_id)
                instance.facebook = payload['facebook']
                instance.twitter = payload['twitter']
                instance.instagram = payload['instagram']
                instance.linkedin = payload['linkedin']
                instance.website = payload['website']
                instance.save()

                for service in support_services:
                    try:
                        service = app_manager_models.SupportServices.objects.get(id=int(service))
                    except ValueError as e:
                        logger.error(e)
                        service = app_manager_models.SupportServices.objects.get(service=service)
                    check = models.InnovationSupportService.objects.filter(service=service,innovation=innovation).exists()
                    if not check:
                        to_create = {
                            "innovation" : innovation,
                            "service" : service
                        }
                        models.InnovationSupportService.objects.create(**to_create)
                return Response("success", status=status.HTTP_200_OK)
            else:                
                socialInstance = models.InnovationSocialLinks.objects.create(**payload)

                for service in support_services:
                    service = app_manager_models.SupportServices.objects.get(id=int(service))
                    to_create = {
                        "innovation" : innovation,
                        "service" : service
                    }
                    models.InnovationSupportService.objects.create(**to_create)
                
                user_util.log_account_activity(
                    authenticated_user, authenticated_user, "Innovation Social Links created", "Id "  + str(socialInstance.id))
                return Response("success", status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False, url_path="remove-support-service",url_name="remove-support-service")
    def remove_support_service(self, request):
        payload = request.data
        # print(payload)
        with transaction.atomic():
            innovation_id = payload['innovation']
            service = payload['service']
            serviceInstance = models.InnovationSupportService.objects.filter(innovation=innovation_id,service__service=service)
            serviceInstance.delete()
            return Response("success", status=status.HTTP_200_OK)


    @action(methods=["GET"], detail=False, url_path="get-innovation-additional-details", url_name="get-innovation-additional-details")
    def get_innovation_additional_details(self, request):
        innovation_id = request.query_params.get('innovation_id')
        if not innovation_id or innovation_id == 'undefined':
            return Response({'details':'Innovation Id Required'},status=status.HTTP_400_BAD_REQUEST)
        try:
            support_service = []
            services =  models.InnovationSupportService.objects.filter(innovation=innovation_id)
            for service in services:
                support_service.append(service.service.service)

            try:
                other_services =  models.OtherInnovationSupportService.objects.get(innovation=innovation_id)
                other_services = other_services.service
            except Exception as e:
                print(e)

            links = models.InnovationSocialLinks.objects.filter(innovation=innovation_id)
            try:
                links = serializers.InnovationSocialLinksSerializer(links[0], many=False).data
            except Exception as e:
                logger.error(e)
                links = []

            links.update({"support_service":support_service,"other_support":other_services})
            # print(links)
            return Response(links, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response({}, status=status.HTTP_200_OK)




    @action(methods=["POST"], detail=False, url_path="complete-innovation",url_name="complete-innovation")
    def complete_innovation(self, request):
        authenticated_user = request.user
        payload = request.data

        with transaction.atomic():
            try:
                innovation_id = payload['innovation_id']
            except:
                return Response({'details':'Invalid Innovation Id'},status=status.HTTP_400_BAD_REQUEST)

            innovation = models.Innovation.objects.get(id=innovation_id)
            
            innovation_status = innovation.status

            if innovation_status == "ONGOING":
                innovation.status = "COMPLETED"
            elif innovation_status == "RESUBMIT":
                innovation.status = "RESUBMITTED"
                try:
                    im_review = models.InnovationManagerReview.objects.get(innovation=innovation,status=True)
                    im_review.status = False
                    im_review.save()
                except Exception as e:
                    logger.error(e)

                try:
                    # SEND NOTIFICATION
                    innovation_name = models.InnovationDetails.objects.get(innovation=innovation).innovation_name.upper()
                    check = models.FinalInnovationManagerReview.objects.filter(innovation=innovation).order_by('-date_created').first()
                    message = f"Innovation: {innovation_name} has been Resubmmited for review"
                    recipient = check.reviewer.first_name
                    subject = "Innovation Application Resubmission"
                    email = check.reviewer.email

                    message_template = read_template("general.html")
                    body = message_template.substitute(NAME=recipient,MESSAGE=message,LINK=settings.FRONTEND)

                    # save notification
                    models.Notifications.objects.create(innovation=innovation,subject=subject,sender=authenticated_user,recipient=check.reviewer, notification=message)

                    # send email
                    user_util.sendmail(email,subject,body)
                except Exception as e:
                    logger.error(e)


            innovation.edit = False
            innovation.save()
            
            user_util.log_account_activity(
                authenticated_user, authenticated_user, f"Innovation {innovation_status}", "Id "  + str(innovation_id))
            return Response("success", status=status.HTTP_200_OK)


    @action(methods=["POST"], detail=False, url_path="innovator-has-read-reviews",url_name="innovator-has-read-reviews")
    def innovator_has_read_reviews(self, request):
        authenticated_user = request.user
        payload = request.data

        with transaction.atomic():
            try:
                innovation_id = payload['innovation_id']
            except:
                return Response({'details':'Invalid Innovation'},status=status.HTTP_400_BAD_REQUEST)            
            
            try:
                innovation = models.Innovation.objects.get(id=innovation_id)
                im_review = models.InnovationManagerReview.objects.get(innovation=innovation,status=True)
                im_review.status = False
                im_review.save()
            except Exception as e:
                logger.error(e)
            
            user_util.log_account_activity(
                authenticated_user, authenticated_user, f"Innovator has reviewed IM reviews", "Id "  + str(innovation_id))
            return Response("success", status=status.HTTP_200_OK)


    @action(methods=["GET"], detail=False, url_path="innovation-review", url_name="innovation-review")
    def innovation_review(self, request):
        innovation_id = request.query_params.get('innovation_id')
        try:
            innovation = models.Innovation.objects.get(id=innovation_id)
            innovation = serializers.FullInnovationSerializer(innovation, many=False, context={"user_id":request.user.id})
            
            return Response(innovation.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response({'details':'Error fetching review'},status=status.HTTP_400_BAD_REQUEST)

class EvaluationViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,JSONParser)
    queryset = models.Evaluation.objects.all().order_by('id')
    serializer_class = serializers.SystemUsersSerializer
    search_fields = ['id', ]

    def get_queryset(self):
        return []

    @action(methods=["POST"], detail=False, url_path="create-evaluation",url_name="create-evaluation")
    def evaluation(self, request):
        authenticated_user = request.user
        payload = request.data

        serializer = serializers.CustomCreateEvaluationSerializer(data=payload, many=False)
        if serializer.is_valid():
            with transaction.atomic():
                try:
                    innovation_id = payload['innovation']
                    innovation = models.Innovation.objects.get(id=innovation_id)
                    payload['innovation'] = innovation                   

                    role = None
                    if innovation.stage == 'IV':
                        role = 'INTERNAL_EVALUATOR'
                    elif innovation.stage == 'V':
                        role = 'SUBJECT_MATTER_EVALUATOR'
                    elif innovation.stage == 'VI':
                        role = 'EXTERNAL_EVALUATOR'

                    payload.update({"evaluator": authenticated_user, "role": role})

                    update = models.Evaluation.objects.filter(innovation=innovation_id,evaluator=authenticated_user).exists()
                except Exception as e:
                    logger.error(e)
                    return Response({"details": "Invalid Innovation Id"}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    for key in payload:
                        if 'score' in key:
                            payload[key] = int(payload[key])
                except Exception as e:
                    logger.error(e)
                
                if update:
                    return Response("success", status=status.HTTP_200_OK) #TODO: remove
                    del payload['innovation']
                    models.Evaluation.objects.filter(innovation=innovation_id).update(**payload)
                    action = "Updated"
                else:
                    newinstance = models.Evaluation.objects.create(**payload)
                    innovation.status = "UNDER_REVIEW"
                    innovation.save()
                    action = "Created"
                
                try:
                    # SEND NOTIFICATION
                    group = models.Group.objects.filter(innovation=innovation,role=role).order_by('-date_created').first()
                    innovation_name = models.InnovationDetails.objects.get(innovation=innovation_id).innovation_name
                    notification = f"Innovation {innovation_name}: has been successfully reviewed by assigned {role} {authenticated_user.first_name} {authenticated_user.first_name}"

                    subject = "Application Reviewed"
                    first_name = group.creator.first_name
                    email = group.creator.email

                    message_template = read_template("general.html")
                    message = message_template.substitute(NAME=first_name,MESSAGE=notification,LINK=settings.FRONTEND)

                    # save notification
                    models.Notifications.objects.create(innovation=innovation,subject=subject,recipient=group.creator, sender=authenticated_user, notification=notification)

                    # send email
                    user_util.sendmail(email,subject,message)
                except Exception as e:
                    logger.error(e)  
               
                user_util.log_account_activity(
                    authenticated_user, authenticated_user, f"Evaluation {action}. Id: " + str(innovation_id) , f"Evaluation {action} Executed")
                return Response("success", status=status.HTTP_200_OK)
        else:
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["GET"], detail=False, url_path="is-evaluated", url_name="is-evaluated")
    def is_evaluated(self, request):
        innovation_id = request.query_params.get('innovation_id')
        authenticated_user = request.user
        try:
            try:
                innovation = models.Evaluation.objects.get(innovation=innovation_id,evaluator=authenticated_user)
            except Exception as e:
                logger.error(e)
                return Response({"status":False}, status=status.HTTP_200_OK)
            innovation = serializers.CreateEvaluationSerializer(innovation, many=False).data
            if innovation:
                innovation.update({"status":True})
            else:
                innovation = {
                    "status":False
                }            
            return Response(innovation, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response({'details':'Error Fetching Evaluated'},status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["GET"], detail=False, url_path="evaluated-innovation", url_name="evaluated-innovation")
    def evaluated_innovation(self, request):
        innovation_id = request.query_params.get('innovation_id')
        evaluator_id = request.query_params.get('evaluator_id')
        try:
            try:
                innovation = models.Evaluation.objects.get(innovation=innovation_id,evaluator_id=evaluator_id)
            except Exception as e:
                logger.error(e)
                return Response({"status":False}, status=status.HTTP_200_OK)
            innovation = serializers.CreateEvaluationSerializer(innovation, many=False).data
            if innovation:
                innovation.update({"status":True})
            else:
                innovation = {
                    "status":False
                }            
            return Response(innovation, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response({'details':'Error Fetching Evaluated'},status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["POST"], detail=False, url_path="create-note",url_name="create-note")
    def note(self, request):
        authenticated_user = request.user
        payload = request.data
        serializer = serializers.CreateNoteSerializer(data=payload, many=False)
        if serializer.is_valid():
            with transaction.atomic():
                try:
                    innovation_id = payload['innovation']
                    innovation = models.Innovation.objects.get(id=innovation_id)
                    payload['innovation'] = innovation
                    payload['created_by'] = authenticated_user
                    if payload['id'] == '':
                        del payload['id']
                except Exception as e:
                    logger.error(e)
                    return Response({"details": "Invalid Innovation Id"}, status=status.HTTP_400_BAD_REQUEST)
                
                try:
                    note_id = payload['id']
                    noteInstance = models.Note.objects.get(id=note_id)
                    noteInstance.title = payload['title']
                    noteInstance.note = payload['note']
                    noteInstance.save()
                    action = 'Edited'
                    instance_id = note_id
                except Exception as e:
                    logger.error(e)
                    newinstance = models.Note.objects.create(**payload)
                    instance_id = newinstance.id
                    action = 'Created'
               
                user_util.log_account_activity(
                    authenticated_user, authenticated_user, f"Note {action}. Id: " + str(instance_id) , f"Note For {innovation_id} ")
                return Response("success", status=status.HTTP_200_OK)
        else:
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            

    @action(methods=["GET"], detail=False, url_path="get-notes", url_name="get-notes")
    def get_notes(self, request):
        authenticated_user = request.user
        try:
            notes = models.Note.objects.filter(created_by=authenticated_user, status=True).order_by('-date_created')
     
            notes = serializers.NoteSerializer(notes, many=True).data
            
            return Response(notes, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response({'details':'Error Fetching Notes'},status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["POST"], detail=False, url_path="delete-note", url_name="delete-note")
    def delete_note(self, request):
        authenticated_user = request.user
        payload = request.data

        serializer = serializers.DeleteNoteSerializer(data=payload, many=False)
        if serializer.is_valid():
            with transaction.atomic():     
                try:
                    note_id = payload['note_id']
                    noteInstance = models.Note.objects.get(id=note_id)
                    noteInstance.status = False
                    noteInstance.save()
                except Exception as e:
                    logger.error(e)
                    return Response({"details": "Error Deleting Note"}, status=status.HTTP_400_BAD_REQUEST)
               
                user_util.log_account_activity(
                    authenticated_user, authenticated_user, f"Note Deleted. Id: " + str(note_id) , f"Note For {noteInstance.innovation.id} ")
                return Response("success", status=status.HTTP_200_OK)
        else:
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["POST"], detail=False, url_path="create-assignment",url_name="create-assignment")
    def assignment(self, request):
        authenticated_user = request.user
        payload = request.data['payload']
        payload = json.loads(payload)

        serializer = serializers.CreateAssignmentSerializer(data=payload, many=False)
        if serializer.is_valid():
            with transaction.atomic():
                try:
                    innovation_id = payload['innovation']
                    innovation = models.Innovation.objects.get(id=innovation_id)
                    payload['innovation'] = innovation
                    payload['created_by'] = authenticated_user
                    if payload['id'] == '':
                        del payload['id']
                except Exception as e:
                    logger.error(e)
                    return Response({"details": "Invalid Innovation Id"}, status=status.HTTP_400_BAD_REQUEST)

                file_available = False
                try:
                    for f in request.FILES.getlist('document'):
                        if f:
                            # print("FIle name", f.name)
                            payload['file'] = f
                            file_available = True
                except Exception as e:
                    logger.error(e)
                        
                
                try:
                    assignment_id = payload['id']
                    assignmentInstance = models.Assignment.objects.get(id=assignment_id)
                    assignmentInstance.title = payload['title']
                    assignmentInstance.description = payload['description']
                    assignmentInstance.deadline = payload['deadline']
                    if file_available:
                        assignmentInstance.file = payload['file']
                    assignmentInstance.save()
                    action = 'Edited'
                    instance_id = assignment_id
                except Exception as e:
                    logger.error(e)
                    newinstance = models.Assignment.objects.create(**payload)
                    instance_id = newinstance.id
                    action = 'Created'
               
                user_util.log_account_activity(
                    authenticated_user, authenticated_user, f"Assignment {action}. Id: " + str(instance_id) , f"Assignment For {innovation_id} ")
                return Response("success", status=status.HTTP_200_OK)
        else:
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
    @action(methods=["POST"], detail=False, url_path="create-assignment-response",url_name="create-assignment-response")
    def assignment_response(self, request):
        authenticated_user = request.user
        payload = request.data['payload']
        payload = json.loads(payload)

        serializer = serializers.CreateAssignmentResponseSerializer(data=payload, many=False)
        if serializer.is_valid():
            with transaction.atomic():
                try:
                    assignment_id = payload['assignment_id']
                    assignment = models.Assignment.objects.get(id=assignment_id)
                    payload['assignment'] = assignment
                except Exception as e:
                    logger.error(e)
                    return Response({"details": "Invalid Assignment"}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    for f in request.FILES.getlist('document'):
                        if f:
                            payload['file'] = f
                except Exception as e:
                    logger.error(e)
                        
                
                newinstance = models.AssignmentResponse.objects.create(**payload)
                instance_id = newinstance.id
                action = 'Created'
               
                user_util.log_account_activity(
                    authenticated_user, authenticated_user, f"Assignment Response {action}. Id: " + str(instance_id) , f"Assignment For {assignment_id} ")
                return Response("success", status=status.HTTP_200_OK)
        else:
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            



    @action(methods=["GET"], detail=False, url_path="get-assignments", url_name="get-assignments")
    def get_assignments(self, request):
        authenticated_user = request.user
        try:
            assignments = models.Assignment.objects.filter(created_by=authenticated_user, status=True).order_by('-date_created')     
            assignments = serializers.AssignmentSerializer(assignments, many=True).data            
            return Response(assignments, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response({'details':'Error Fetching Assignments'},status=status.HTTP_400_BAD_REQUEST)

    
    @action(methods=["GET"], detail=False, url_path="get-innovator-assignments", url_name="get-innovator-assignments")
    def get_innovator_assignments(self, request):
        authenticated_user = request.user
        my_innovations = models.Innovation.objects.filter(creator=authenticated_user)
        innovation_ids = []
        if my_innovations:
            for innovation in my_innovations:
                innovation_ids.append(innovation.id)
        else:
            return Response({}, status=status.HTTP_200_OK)

        try:
            assignments = models.Assignment.objects.filter(innovation__in=innovation_ids, status=True).order_by('-date_created')     
            assignments = serializers.AssignmentSerializer(assignments, many=True).data            
            return Response(assignments, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response({'details':'Error Fetching Assignments'},status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["POST"], detail=False, url_path="delete-assignment", url_name="delete-assignment")
    def delete_assignment(self, request):
        authenticated_user = request.user
        payload = request.data

        serializer = serializers.DeleteAssignmentSerializer(data=payload, many=False)
        if serializer.is_valid():
            with transaction.atomic():     
                try:
                    assignment_id = payload['assignment_id']
                    assignmentInstance = models.Assignment.objects.get(id=assignment_id)
                    assignmentInstance.status = False
                    assignmentInstance.save()
                except Exception as e:
                    logger.error(e)
                    return Response({"details": "Error Deleting Assignment"}, status=status.HTTP_400_BAD_REQUEST)
               
                user_util.log_account_activity(
                    authenticated_user, authenticated_user, f"Assignment Deleted. Id: " + str(assignment_id) , f"Assignment For {assignmentInstance.innovation.id} ")
                return Response("success", status=status.HTTP_200_OK)
        else:
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["POST"], detail=False, url_path="create-group",url_name="create-group")
    def group(self, request):
        authenticated_user = request.user
        payload = request.data
        # print(payload)

        serializer = serializers.CreateGroupSerializer(data=payload, many=False)
        if serializer.is_valid():
            with transaction.atomic():
                try:
                    innovation_id = payload['innovation']
                    innovation = models.Innovation.objects.get(id=innovation_id)
                    innovation_name = models.InnovationDetails.objects.get(innovation=innovation).innovation_name.upper()
                    payload['innovation'] = innovation
                    payload['creator'] = authenticated_user
                    assignees = payload['assignees']
                    lead = payload['lead']
                    role = payload['role']
                    reassign = payload['reassign']
                    del payload['assignees']
                    del payload['lead']
                    del payload['reassign']
                except Exception as e:
                    logger.error(e)
                    return Response({"details": "Invalid Innovation Id"}, status=status.HTTP_400_BAD_REQUEST)   

                group_exists = models.Group.objects.filter(innovation=innovation, status=True)
                if not reassign:
                    if group_exists:                    
                        for group in group_exists:
                            group.status = False
                            group.save()    

                    groupinstance = models.Group.objects.create(**payload)
                else:
                    groupinstance = group_exists.first()
                    
                if role == "CHIEF_EVALUATOR":
                    assignees = get_user_model().objects.filter(groups__name=role)

                for assignee in assignees:
                    if role == "CHIEF_EVALUATOR":
                        member = assignee
                    else:
                        member = get_user_model().objects.get(id=assignee)
                    is_existing =  models.GroupMember.objects.filter(group=groupinstance,member=member).exists()
                    if not is_existing:
                        user_util.revoke_role(role,assignee)
                        if assignee == lead:
                            models.GroupMember.objects.create(group=groupinstance,member=member,is_lead=True)
                            message = f"You have been assigned a team of evaluators for innovation: {innovation_name} as {role}"
                        else:
                            models.GroupMember.objects.create(group=groupinstance,member=member)
                            message = f"You have been assigned an evaluation role for innovation: {innovation_name} as {role}"

                        try:
                            # SEND NOTIFICATION
                            subject = "Assigned Evaluation Role"
                            email = member.email

                            message_template = read_template("general.html")
                            body = message_template.substitute(NAME=member.first_name,MESSAGE=message,LINK=settings.FRONTEND)

                            # save notification
                            models.Notifications.objects.create(innovation=innovation,subject=subject,sender=authenticated_user,recipient=member, notification=message)

                            # send email
                            user_util.sendmail(email,subject,body)
                        except Exception as e:
                            logger.error(e)

                assign_role = user_util.award_role(role,lead)

                if not assign_role:
                    return Response({"details": "Role Assigning Failed"}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    assignees = ", ".join(assignees)   
                except Exception as e:
                    pass

                if role == 'INTERNAL_EVALUATOR':    
                    innovation.stage = 'IV'
                    fim = models.FinalInnovationManagerReview.objects.filter(innovation=innovation, status=True)
                    if fim:
                        for review in fim:
                            review.status = False
                            review.save()
                elif role == 'SUBJECT_MATTER_EVALUATOR':
                    innovation.stage = 'V'
                elif role == 'EXTERNAL_EVALUATOR':
                    innovation.stage = 'VI'
                elif role == 'JUNIOR_OFFICER':
                    innovation.stage = 'II'
                    innovation.status = 'UNDER_REVIEW'
                elif role == 'CHIEF_EVALUATOR':
                    innovation.stage = 'VII'
                innovation.save() 


                user_util.log_account_activity(
                    authenticated_user, authenticated_user, f"Group Created. Id: " + str(groupinstance.id) , f"Group members : {assignees} ")
                return Response("success", status=status.HTTP_200_OK)
        else:
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["POST"], detail=False, url_path="create-review",url_name="create-review")
    def review(self, request):
        authenticated_user = request.user
        payload = request.data

        roles = user_util.fetchusergroups(authenticated_user.id)

        serializer = serializers.CreateReviewSerializer(data=payload, many=False)
        if serializer.is_valid():
            with transaction.atomic():
                try:
                    innovation_id = payload['innovation']
                    innovation = models.Innovation.objects.get(id=innovation_id)
                    payload['innovation'] = innovation
                    payload['reviewer'] = authenticated_user
                    action = payload['action']
                    is_final = payload['is_final']
                    if 'LEAD_JUNIOR_OFFICER' in roles:
                        payload['is_lead'] = True
                except Exception as e:
                    logger.error(e)
                    return Response({"details": "Invalid Innovation Id"}, status=status.HTTP_400_BAD_REQUEST)  

                check = models.InnovationReview.objects.filter(reviewer=authenticated_user,innovation=innovation)
                
                if action != 'DROPPED':
                    innovation.stage = "II"
                else:
                    innovation.status = 'DROPPED'
                innovation.save()

                if check:
                    reviewInstance = check.first()
                    if is_final:
                        if not reviewInstance.is_final:
                            action = "JO Final Review Created"
                            reviewInstance = models.InnovationReview.objects.create(**payload)                    
                    # reviewInstance.review = payload['review']
                    # reviewInstance.action = payload['action']
                    # reviewInstance.save()
                    # action = "Updated"
                else:
                    action = "Created"
                    reviewInstance = models.InnovationReview.objects.create(**payload)   

                    try:
                        # SEND NOTIFICATION
                        group = models.Group.objects.filter(innovation=innovation,role="JUNIOR_OFFICER").order_by('-date_created').first()
                        innovation_name = models.InnovationDetails.objects.get(innovation=innovation_id).innovation_name
                        notification = f"Innovation {innovation_name}: has been successfully reviewed by assigned Junior Officer {authenticated_user.first_name} {authenticated_user.last_name}"

                        subject = "Application Reviewed"
                        first_name = group.creator.first_name
                        email = group.creator.email

                        message_template = read_template("general.html")
                        message = message_template.substitute(NAME=first_name,MESSAGE=notification,LINK=settings.FRONTEND)

                        # save notification
                        models.Notifications.objects.create(innovation=innovation,subject=subject,recipient=group.creator, sender=authenticated_user, notification=notification)

                        # send email
                        user_util.sendmail(email,subject,message)
                    except Exception as e:
                        logger.error(e)       

                user_util.log_account_activity(
                    authenticated_user, authenticated_user, f"Junior Innovation Review {action}. Id: " + str(reviewInstance.id) , f"Junior Innovation Review")
                return Response("success", status=status.HTTP_200_OK)
        else:
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["POST"], detail=False, url_path="create-final-evaluators-comment",url_name="create-final-evaluators-comment")
    def final_evaluators_comment(self, request):
        authenticated_user = request.user
        payload = request.data

        roles = user_util.fetchusergroups(authenticated_user.id)

        serializer = serializers.CreateReviewSerializer(data=payload, many=False)
        if serializer.is_valid():
            with transaction.atomic():
                try:
                    innovation_id = payload['innovation']
                    innovation = models.Innovation.objects.get(id=innovation_id)

                    stage = innovation.stage
                    if stage == 'IV':
                        role = 'INTERNAL_EVALUATOR'
                    elif stage == 'V':
                        role = 'SUBJECT_MATTER_EVALUATOR'
                    elif stage == 'VI':
                        role = 'EXTERNAL_EVALUATOR'
                    elif stage == 'VII':
                        role = 'CHIEF_EVALUATOR'
                    else:
                        role = None
                        logger.error("Unkwnow Role. Stage = ", stage)
                        return Response({"details": "Unkwnow Role"}, status=status.HTTP_400_BAD_REQUEST)                    
                

                    payload['innovation'] = innovation
                    payload['reviewer'] = authenticated_user
                    payload['stage'] = stage
                    action = payload['action']
                    del payload['is_final']

                except Exception as e:
                    logger.error(e)
                    return Response({"details": "Invalid Innovation"}, status=status.HTTP_400_BAD_REQUEST)  

                check = models.FinalEvaluatorsComment.objects.filter(reviewer=authenticated_user,innovation=innovation)
                
                if action == 'DROPPED' or action == 'DROP':
                    innovation.status = 'DROPPED'
                    msg_to_innovator = "Your innovation has gone through our 6 stages of evaluation and has been found to be not viable. Please log on  to our platform to review the final report and evaluators recommendations.<br>\
                    You are not eligible for our Innovation Management Support program. <br>\
                    Please contact the IENAfrica Innovation Manager to schedule a meeting for more details."
                elif action == 'APPROVE':
                    innovation.status = 'APPROVED'
                    msg_to_innovator = "Your innovation has gone through our 6 stages of evaluation and has been found to be viable. Please log on to our platform to review the final report and evaluators recommendations.<br>\
                    With this positive evaluation outcome you are now eligible for our Innovation Management Support program.<br>\
                    Please contact the IENAfrica Innovation Manager to schedule a meeting for more details."
                else:
                    innovation.status = 'EVALUATED'
                innovation.save()
     
                if not check:
                    action_text = "Final evaluator comment Created by " + role
                    reviewInstance = models.FinalEvaluatorsComment.objects.create(**payload)   

                    try:
                        # SEND NOTIFICATION
                        group = models.Group.objects.filter(innovation=innovation,stage=stage).order_by('-date_created').first()
                        innovation_name = models.InnovationDetails.objects.get(innovation=innovation_id).innovation_name
                        notification = f"Innovation {innovation_name}: has been successfully reviewed by assigned  {role} {authenticated_user.first_name} {authenticated_user.last_name}, with a final action of {action}"

                        subject = "Application Reviewed"
                        first_name = group.creator.first_name
                        email = group.creator.email

                        message_template = read_template("general.html")
                        message = message_template.substitute(NAME=first_name,MESSAGE=notification,LINK=settings.FRONTEND)

                        # save notification
                        models.Notifications.objects.create(innovation=innovation,subject=subject,recipient=group.creator, sender=authenticated_user, notification=notification)

                        # send email
                        user_util.sendmail(email,subject,message)

                    except Exception as e:
                        logger.error(e)   

                if action == 'DROPPED' or action == 'DROP' or action == 'APPROVE':
                    if role == 'CHIEF_EVALUATOR':
                        try:
                            # SEND NOTIFICATION
                            # Message to Innovator
                            innovator_fname = innovation.creator.first_name
                            innovator_email = innovation.creator.email
                            subject = "Your Innovation Status"

                            message_template = read_template("general.html")
                            message = message_template.substitute(NAME=innovator_fname,MESSAGE=msg_to_innovator,LINK=settings.FRONTEND)

                            # save notification
                            models.Notifications.objects.create(innovation=innovation,subject=subject,recipient=innovation.creator, sender=authenticated_user, notification=msg_to_innovator)

                            # send email
                            user_util.sendmail(innovator_email,subject,message)

                        except Exception as e:
                            logger.error(e)    

                        # Save pending final report
                        models.PendingFinalReport.objects.create(innovation=innovation)

                user_util.log_account_activity(
                    authenticated_user, authenticated_user, f"{action_text}. Id: " + str(reviewInstance.id) , f"{role} Innovation Review")
                return Response("success", status=status.HTTP_200_OK)
        else:
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    
    @action(methods=["GET"], detail=False, url_path="get-my-innovation-reviews", url_name="get-my-innovation-reviews")
    def get_my_innovation_reviews(self, request):
        innovation_id = request.query_params.get('innovation_id')
        authenticated_user = request.user
        try:
            reviews = models.InnovationReview.objects.get(reviewer=authenticated_user, innovation=innovation_id, status=True)
            reviews = serializers.ReviewSerializer(reviews, many=False).data  
        except Exception as e:
            logger.error(e)
            reviews = []
        return Response(reviews, status=status.HTTP_200_OK)


    @action(methods=["POST"], detail=False, url_path="create-innovation-manager-review",url_name="create-innovation-manager-review")
    def innovation_manager_review(self, request):
        authenticated_user = request.user
        payload = request.data
        review = {"review":payload, "innovation":payload['innovation']}

        serializer = serializers.CreateInnovationManagerReviewSerializer(data=review, many=False)
        if serializer.is_valid():
            with transaction.atomic():
                try:
                    action_status = payload['action']
                    innovation_id = payload['innovation']
                    innovation = models.Innovation.objects.get(id=innovation_id)

                    del payload['innovation']

                    reviewer = authenticated_user
                    review = payload
                    payload = {
                        "innovation" : innovation,
                        "reviewer" : reviewer,
                        "review" : review,
                    }
                except Exception as e:
                    logger.error(e)
                    return Response({"details": "Invalid Innovation Id"}, status=status.HTTP_400_BAD_REQUEST)  
                    
                check = models.InnovationManagerReview.objects.filter(reviewer=authenticated_user,innovation=innovation)

                if check:
                    reviewInstance = check.first()
                    reviewInstance.review = payload['review']
                    reviewInstance.save()
                    action = "Updated"
                else:
                    action = "Created"
                    reviewInstance = models.InnovationManagerReview.objects.create(**payload) 
                
                if innovation.stage == "II":
                    innovation.stage = "III"

                if action_status == "RESUBMIT":
                    innovation.edit = True
                    innovation.status = "RESUBMIT"

                innovation.save()   

                junior_review = models.InnovationReview.objects.filter(innovation=innovation, status=True)   
                for review in junior_review:
                    review.status = False
                    review.save() 

                group = models.Group.objects.get(innovation=innovation, role='JUNIOR_OFFICER', status=True)
                group.status = False
                group.save()

                try:
                    # SEND NOTIFICATION
                    if action_status == "RESUBMIT":
                        innovation_name = models.InnovationDetails.objects.get(innovation=innovation.id).innovation_name
                        notification = f"Following review of your innovation application: {innovation_name}. We request you to Resubmit after making all the necessary changes as advised"

                        subject = "Application Resubmission"
                        first_name = innovation.creator.first_name
                        email = innovation.creator.email

                        message_template = read_template("general.html")
                        message = message_template.substitute(NAME=first_name,MESSAGE=notification,LINK=settings.FRONTEND)

                        # save notification
                        models.Notifications.objects.create(innovation=innovation,subject=subject,recipient=innovation.creator, sender=authenticated_user, notification=notification)

                        # send email
                        user_util.sendmail(email,subject,message)
                except Exception as e:
                    logger.error(e)

                user_util.log_account_activity(
                    authenticated_user, authenticated_user, f"Innovation Manager Review {action}. Id: " + str(reviewInstance.id) , f"Innovation Manager Review")

                return Response("success", status=status.HTTP_200_OK)
        else:
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["GET"], detail=False, url_path="get-innovation-manager-review", url_name="get-innovation-manager-review")
    def get_innovation_manager_reviews(self, request):
        innovation_id = request.query_params.get('innovation_id')
        authenticated_user = request.user
        try:
            reviews = models.InnovationManagerReview.objects.get(reviewer=authenticated_user, innovation=innovation_id, status=True)
            reviews = serializers.InnovationManagerReviewSerializer(reviews, many=False).data  
        except Exception as e:
            logger.error(e)
            reviews = {}
        return Response(reviews, status=status.HTTP_200_OK)



    @action(methods=["POST"], detail=False, url_path="create-final-innovation-manager-review",url_name="create-final-innovation-manager-review")
    def final_innovation_manager_review(self, request):
        authenticated_user = request.user
        payload = request.data

        serializer = serializers.CreateReviewSerializer(data=payload, many=False)
        if serializer.is_valid():
            with transaction.atomic():
                try:
                    innovation_id = payload['innovation']
                    innovation = models.Innovation.objects.get(id=innovation_id)
                    payload['innovation'] = innovation
                    payload['reviewer'] = authenticated_user
                    action = payload['action']
                    review = payload['review']
                    innovation_name = models.InnovationDetails.objects.get(innovation=innovation).innovation_name
                except Exception as e:
                    logger.error(e)
                    return Response({"details": "Invalid Innovation Id"}, status=status.HTTP_400_BAD_REQUEST) 

                check = models.FinalInnovationManagerReview.objects.filter(reviewer=authenticated_user,innovation=innovation, status=True)

                message = ""

                if action == 'DROP':
                    innovation.status = 'DROPPED'                    
                    message = f"After thorough review of {innovation_name}, we are sorry to inform you that we shall not be able to proceed with your innovation at this time. \nWe appreciate your effort, trying to make the world a better place. \nBelow is a copy of reviewer final comment: \n\n {review} \n\n"
                else:
                    if action == 'INVITATION_TO_PRESENT':
                        innovation.status = 'INVITATION_TO_PRESENT'
                        message = f"After thorough review of {innovation_name}, we would like to invite you to do a presentation, to enable us understand your innovation further.\n\n"
                    elif action == 'RESUBMIT':
                        innovation.status = 'RESUBMIT'
                        innovation.edit = True
                        message = f"After thorough review of your innovation {innovation_name}, we have recommended appropriate changes.\nPlease effect them and Resubmit.\n\n"
                    elif action == 'APPROVED':
                        innovation.status = 'APPROVED'
                        innovation.edit = True
                        message = f"Congratulations, your innovation {innovation_name} has been approved!\n\n"
                    else:
                        innovation.status = 'UNDER_REVIEW'

                    if innovation.stage == "II":
                        innovation.stage = "III"
                    elif innovation.stage == "III":
                        innovation.stage = "IV"
                    elif innovation.stage == "IV":
                        innovation.stage = "V"
                        
                innovation.save()

                if check:
                    reviewInstance = check.first()
                    reviewInstance.review = payload['review']
                    reviewInstance.action = payload['action']
                    reviewInstance.save()
                    action = "Updated"
                else:
                    action = "Created"
                    reviewInstance = models.FinalInnovationManagerReview.objects.create(**payload)    

                if action != 'PROCEED' or action != 'UNDER_REVIEW':
                    # SEND NOTIFICATION
                    recipient = innovation.creator.first_name
                    subject = "Your Innovation Status"
                    email = innovation.creator.email
                    try:

                        message_template = read_template("general.html")
                        body = message_template.substitute(NAME=recipient,MESSAGE=message,LINK=settings.FRONTEND)

                        # save notification
                        models.Notifications.objects.create(innovation=innovation,subject=subject,recipient=innovation.creator,sender=authenticated_user, notification=message)

                        # send email
                        user_util.sendmail(email,subject,body)
                    except Exception as e:
                        logger.error(e)

                user_util.log_account_activity(
                    authenticated_user, authenticated_user, f"Final Innovation Manager Review {action}. Id: " + str(reviewInstance.id) , f"Innovation Manager Final Review")
                return Response("success", status=status.HTTP_200_OK)
        else:
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["GET"], detail=False, url_path="get-notifications", url_name="get-notifications")
    def get_notifications(self, request):
        try:
            authenticated_user = request.user
               
            try:
                notification = models.Notifications.objects.filter(recipient=authenticated_user, is_seen=False).order_by('-date_created')
                notification = serializers.NotificationsSerializer(notification, many=True).data  
            except Exception as e:
                logger.error(e)
                notification = {}
            return Response(notification, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)


    @action(methods=["GET"], detail=False, url_path="mark-notifications-as-read", url_name="mark-notifications-as-read")
    def notifications_as_read(self, request):
        try:
            authenticated_user = request.user
               
            try:
                notifications = models.Notifications.objects.filter(recipient=authenticated_user, is_seen=False).order_by('-date_created')
                for notification in notifications:
                    notification.is_seen = True
                    notification.save()
            except Exception as e:
                logger.error(e)
            return Response('success', status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)