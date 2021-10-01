import json
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

import innovation





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
            return Response({'details':'Error fetching'},status=status.HTTP_400_BAD_REQUEST)

    
    @action(methods=["GET"], detail=False, url_path="innovations", url_name="innovations")
    def innovations(self, request):
        try:
            innovation = models.Innovation.objects.exclude(status__in=('DROPED','ONGOING'))
            # print(innovation)
            if innovation:
                innovations = serializers.FullInnovationSerializer(innovation, many=True ,context={"user_id":request.user.id}).data

                return Response(innovations, status=status.HTTP_200_OK)
            else:
                return Response({}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'details':'Error Fetching Innovations'},status=status.HTTP_400_BAD_REQUEST)

    
    @action(methods=["GET"], detail=False, url_path="assigned-innovations", url_name="assigned-innovations")
    def assigned_innovations(self, request):
        user = request.user
        try:
            innovation_pks = []

            innovations = models.GroupMember.objects.filter(member=user)
            for innovation in innovations:
                innovation_pks.append(innovation.group.innovation.id)

            innovation = models.Innovation.objects.filter(pk__in=innovation_pks).exclude(status__in=('DROPED','ONGOING'))
            
            if innovation:
                innovations = serializers.FullInnovationSerializer(innovation, many=True, context={"user_id":request.user.id}).data

                return Response(innovations, status=status.HTTP_200_OK)
            else:
                return Response({}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'details':'Error Fetching Innovations'},status=status.HTTP_400_BAD_REQUEST)

    
    @action(methods=["GET"], detail=False, url_path="my-innovations", url_name="my-innovations")
    def my_innovations(self, request):
        try:
            innovation = models.Innovation.objects.filter(creator=request.user)
            innovation = serializers.FullInnovationSerializer(innovation, many=True)
            
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

                print(payload)
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
                print(payload)
                try:
                    innovation = payload['innovation']
                    innovation = models.Innovation.objects.get(id=innovation)
                except Exception as e:
                    print(e)
                    return Response({'details': 'Missing Innovation Id'},status=status.HTTP_400_BAD_REQUEST )

                try:
                    details_id = payload['details_id']
                    details_instance = models.InnovationDetails.objects.get(id=details_id)
                except Exception as e:
                    print(e)
                    return Response({'details': 'Missing Details Id'},status=status.HTTP_400_BAD_REQUEST )

                try:
                    industry = payload['industry']
                    industry = app_manager_models.Industry.objects.get(id=industry)
                    details_instance.industry = industry
                except Exception as e:
                    print(e)

                try:
                    development_stage = payload['development_stage']
                    development_stage = app_manager_models.DevelopmentStage.objects.get(id=development_stage)
                    details_instance.development_stage = development_stage
                except Exception as e:
                    print(e)

                intellectual_property = payload['intellectual_property']
                if intellectual_property != 'None' or intellectual_property != 'None of the above':
                    try:
                        intellectual_property = app_manager_models.IntellectualProperty.objects.get(id=intellectual_property)
                        details_instance.intellectual_property = intellectual_property
                    except Exception as e:
                        print(e)
                
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
                            print(e)
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
            print("details", details)
            details = serializers.InnovationDetailsSerializer(details, many=False)
            
            return Response(details.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
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
                innovation_exists = models.InnovationInformation.objects.filter(innovation=innovation_id).exists()
                innovation = models.Innovation.objects.get(id=innovation_id)
                payload['innovation'] = innovation

                if innovation_exists:
                    instance = models.InnovationInformation.objects.get(innovation=innovation_id)
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
            print(e)
            return Response({'status': False}, status=status.HTTP_200_OK)


    @action(methods=["POST"], detail=False, url_path="innovation-additional-details",url_name="innovation-additional-details")
    def innovation_additional_details(self, request):
        authenticated_user = request.user
        payload = request.data
        print(payload)
        with transaction.atomic():
            innovation_id = payload['innovation']
            innovation = models.Innovation.objects.get(id=innovation_id)
            payload['innovation'] = innovation
            print("innovation: ",innovation.__dict__)

            support_services = []
                
            try:
                support_services = payload['support_service']
            except Exception as e:
                print(e)

            del payload['support_service']


            links_exists =  models.InnovationSocialLinks.objects.filter(innovation=innovation_id).exists()
            print("links_exists: ", links_exists)
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
                        print(e)
                        service = app_manager_models.SupportServices.objects.get(service=service)
                    if models.InnovationSupportService.objects.filter(service=service).exists():
                        pass
                    else:
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

            links = models.InnovationSocialLinks.objects.filter(innovation=innovation_id)
            try:
                links = serializers.InnovationSocialLinksSerializer(links[0], many=False).data
            except Exception as e:
                print(e)
                links = []
            links.update({"support_service":support_service})
            # print(links)
            return Response(links, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
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
                    print(e)

            innovation.edit = False
            innovation.save()
            
            user_util.log_account_activity(
                authenticated_user, authenticated_user, f"Innovation {innovation_status}", "Id "  + str(innovation_id))
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
                    print(e)
                    return Response({"details": "Invalid Innovation Id"}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    for key in payload:
                        if 'score' in key:
                            payload[key] = int(payload[key])
                except Exception as e:
                    print(e)
                
                if update:
                    del payload['innovation']
                    models.Evaluation.objects.filter(innovation=innovation_id).update(**payload)
                    action = "Updated"
                else:
                    newinstance = models.Evaluation.objects.create(**payload)
                    innovation.status = "UNDER_REVIEW"
                    innovation.save()
                    action = "Created"
               
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
                print(e)
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
            print(e)
            return Response({'details':'Error Fetching Evaluated'},status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["GET"], detail=False, url_path="evaluated-innovation", url_name="evaluated-innovation")
    def evaluated_innovation(self, request):
        innovation_id = request.query_params.get('innovation_id')
        evaluator_id = request.query_params.get('evaluator_id')
        try:
            try:
                innovation = models.Evaluation.objects.get(innovation=innovation_id,evaluator_id=evaluator_id)
            except Exception as e:
                print(e)
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
            print(e)
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
                    print(e)
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
                    print(e)
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
            print(e)
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
                    print(e)
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
                    print(e)
                    return Response({"details": "Invalid Innovation Id"}, status=status.HTTP_400_BAD_REQUEST)

                file_available = False
                try:
                    for f in request.FILES.getlist('document'):
                        if f:
                            print("FIle name", f.name)
                            payload['file'] = f
                            file_available = True
                except Exception as e:
                    print(e)
                        
                
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
                    print(e)
                    newinstance = models.Assignment.objects.create(**payload)
                    instance_id = newinstance.id
                    action = 'Created'
               
                user_util.log_account_activity(
                    authenticated_user, authenticated_user, f"Assignment {action}. Id: " + str(instance_id) , f"Assignment For {innovation_id} ")
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
            print(e)
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
            print(e)
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
                    print(e)
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

        serializer = serializers.CreateGroupSerializer(data=payload, many=False)
        if serializer.is_valid():
            with transaction.atomic():
                try:
                    innovation_id = payload['innovation']
                    innovation = models.Innovation.objects.get(id=innovation_id)
                    payload['innovation'] = innovation
                    payload['creator'] = authenticated_user
                    assignees = payload['assignees']
                    lead = payload['lead']
                    role = payload['role']
                    del payload['assignees']
                    del payload['lead']
                except Exception as e:
                    print(e)
                    return Response({"details": "Invalid Innovation Id"}, status=status.HTTP_400_BAD_REQUEST)   

                group_exists = models.Group.objects.filter(innovation=innovation, status=True)
                if group_exists:
                    for group in group_exists:
                        group.status = False
                        group.save()    

                groupinstance = models.Group.objects.create(**payload)
                
                for assignee in assignees:
                    user_util.revoke_role(role,assignee)
                    member = get_user_model().objects.get(id=assignee)
                    if assignee == lead:
                        models.GroupMember.objects.create(group=groupinstance,member=member,is_lead=True)
                    else:
                        models.GroupMember.objects.create(group=groupinstance,member=member)

                assign_role = user_util.award_role(role,lead)

                if assign_role:
                    print("Role Award Successful")
                else:
                    print("Role Award UnSuccessful")

                assignees = ", ".join(assignees)   

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

        serializer = serializers.CreateReviewSerializer(data=payload, many=False)
        if serializer.is_valid():
            with transaction.atomic():
                try:
                    innovation_id = payload['innovation']
                    innovation = models.Innovation.objects.get(id=innovation_id)
                    payload['innovation'] = innovation
                    payload['reviewer'] = authenticated_user
                    action = payload['action']
                except Exception as e:
                    print(e)
                    return Response({"details": "Invalid Innovation Id"}, status=status.HTTP_400_BAD_REQUEST)  

                check = models.InnovationReview.objects.filter(reviewer=authenticated_user,innovation=innovation)
                
                if action == 'PROCEED':
                    innovation.stage = "II"
                innovation.save()

                if check.exists():
                    reviewInstance = check.first()
                    reviewInstance.review = payload['review']
                    reviewInstance.action = payload['action']
                    reviewInstance.save()
                    action = "Updated"
                else:
                    action = "Created"
                    reviewInstance = models.InnovationReview.objects.create(**payload)          

                user_util.log_account_activity(
                    authenticated_user, authenticated_user, f"Junior Innovation Review {action}. Id: " + str(reviewInstance.id) , f"Junior Innovation Review")
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
            print(e)
            reviews = {}
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
                    print(e)
                    return Response({"details": "Invalid Innovation Id"}, status=status.HTTP_400_BAD_REQUEST)  
                    
                check = models.InnovationManagerReview.objects.filter(reviewer=authenticated_user,innovation=innovation)

                if check.exists():
                    reviewInstance = check.first()
                    reviewInstance.review = payload['review']
                    reviewInstance.save()
                    action = "Updated"
                else:
                    action = "Created"
                    reviewInstance = models.InnovationManagerReview.objects.create(**payload) 

                innovation.edit = True
                innovation.status = "RESUBMIT"
                innovation.save()   

                junior_review = models.InnovationReview.objects.get(innovation=innovation, status=True)   
                junior_review.status = False
                junior_review.save() 

                group = models.Group.objects.get(innovation=innovation, role='JUNIOR_OFFICER', status=True)
                group.status = False
                group.save()

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
            print(e)
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
                    print(e)
                    return Response({"details": "Invalid Innovation Id"}, status=status.HTTP_400_BAD_REQUEST) 

                check = models.FinalInnovationManagerReview.objects.filter(reviewer=authenticated_user,innovation=innovation, status=True)

                message = ""

                if action == 'DROP':
                    innovation.status = 'DROPPED'                    
                    message = f"Dear Innovator, \n After thorough review of {innovation_name}, we are sorry to inform you that we shall not be able to proceed with your innovation at this time. \nWe appreciate your effort, trying to make the world a better place. \nBelow is a copy of reviewer final comment: \n\n {review} \n\n"
                else:
                    if action == 'INVITATION_TO_PRESENT':
                        innovation.status = 'INVITATION_TO_PRESENT'
                        message = f"Dear Innovator, \n After thorough review of {innovation_name}, we would like to invite you to do a presentation, to enable us understand your innovation further.\n\n"
                    elif action == 'RESUBMIT':
                        innovation.status = 'RESUBMIT'
                        innovation.edit = True
                        message = f"Dear Innovator, \n After thorough review of your innovation {innovation_name}, we have recommended appropriate changes.\nPlease effect them and Resubmit.\n\n"
                    elif action == 'APPROVE':
                        innovation.status = 'APPROVED'
                        innovation.edit = True
                        message = f"Dear Innovator, \n Congratulations, ypur innovation {innovation_name} has been approved!\n\n"
                    else:
                        innovation.status = 'UNDER_REVIEW'
                    if innovation.stage == "II":
                        innovation.stage = "III"
                    elif innovation.stage == "III":
                        innovation.stage = "IV"
                    elif innovation.stage == "IV":
                        innovation.stage = "V"
                innovation.save()

                if check.exists():
                    reviewInstance = check.first()
                    reviewInstance.review = payload['review']
                    reviewInstance.action = payload['action']
                    reviewInstance.save()
                    action = "Updated"
                else:
                    action = "Created"
                    reviewInstance = models.FinalInnovationManagerReview.objects.create(**payload)    

                    recipient = innovation.creator.email
                    subject = "Your Innovation Status"

                    if action != 'PROCEED':
                        notify = user_util.sendmail(recipient,subject,message)     
                        if notify:
                            print("Email sent ...") 
                        else:
                            print("Email sending failed ...")

                user_util.log_account_activity(
                    authenticated_user, authenticated_user, f"Final Innovation Manager Review {action}. Id: " + str(reviewInstance.id) , f"Innovation Manager Final Review")
                return Response("success", status=status.HTTP_200_OK)
        else:
            return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)