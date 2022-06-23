import json
import logging
from typing import SupportsAbs
from user_manager.models import Document
from rest_framework.views import APIView
from . import models
from . import serializers 
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


class VotingViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,JSONParser)
    queryset = models.Positions.objects.all().order_by('id')
    serializer_class = serializers.SystemUsersSerializer
    search_fields = ['id', ]

    def get_queryset(self):
        return []

    @action(methods=["GET"], detail=False, url_path="fetch-positions", url_name="fetch-positions")
    def fetch_positions(self, request):
        try:
            positions = models.Positions.objects.all().order_by('name')
            GenericSerializer = serializers.getGenericSerializer(models.Positions)
            generic_serializer = GenericSerializer(positions, many=True)        
            return Response(generic_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            logger.error(e)
            return Response({'details':'Error Fetching Positions'},status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["POST"], detail=False, url_path="create-candidate-position", url_name="create-candidate-position")
    def create_candidate_position(self, request):
        payload = request.data
        authenticated_user = request.user

        # print(payload)

        serializer = serializers.CreateCandidatePositionSerializer(data=payload, many=False)
        if serializer.is_valid():
            authenticated_user = request.user
            with transaction.atomic():
                position = payload['position']  

                try:
                    positionInstance = models.Positions.objects.get(id=position)  
                except(ValidationError, ObjectDoesNotExist):
                    return Response({'details':"Incorrect Position"}, status=status.HTTP_400_BAD_REQUEST)

                is_existing = models.CandidatePosition.objects.filter(candidate=authenticated_user)

                if is_existing:
                    position = is_existing.first()
                    position.position = positionInstance
                    position.save()
                else:
                    raw = {
                        "candidate": authenticated_user, #get_user_model().objects.get(id=authenticated_user.id),
                        "position" : positionInstance
                    }
                    models.CandidatePosition.objects.create(**raw) 

                return Response("success", status=status.HTTP_200_OK)
        else:
            return Response({'details':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["GET"], detail=False, url_path="fetch-candidate-positions", url_name="fetch-candidate-positions")
    def fetch_candidate_positions(self, request):
        try:
            candidates = models.CandidatePosition.objects.all().order_by('date_created')

            serializer = serializers.FetchCandidatePositionSerializer(candidates, many=True)   
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            logger.error(e)
            return Response({'details':'Error Fetching Candidates'},status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["GET"], detail=False, url_path="fetch-candidate-position", url_name="fetch-candidate-position")
    def fetch_candidate_position(self, request):
        request_id = request.query_params.get('request_id')

        if request_id is None:
            request_id = request.user.id
            
        try:
            candidate = models.CandidatePosition.objects.filter(candidate=request_id,status=True)

            if candidate:
                candidate =  candidate.first()
            else:
                return Response([], status=status.HTTP_200_OK) # candidate has no position

            serializer = serializers.FetchCandidatePositionSerializer(candidate, many=False)                     
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            logger.error(e)
            return Response({'details':'Error Fetching Candidate'},status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["POST"], detail=False, url_path="delete-candidate-position", url_name="delete-candidate-position")
    def delete_candidate_position(self, request):            
        try:
            candidate = models.CandidatePosition.objects.get(candidate=request.user)
            candidate.status = False
            candidate.application_status = "DELETED"
            candidate.save()            
            return Response("success", status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response({'details':'Error Fetching Candidates'},status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["POST"], detail=False, url_path="approve-candidate-position", url_name="approve-candidate-position")
    def approve_candidate_position(self, request):  
        payload = request.data     
        serializer = serializers.CandidateApprovalPositionSerializer(data=payload, many=False)
        if serializer.is_valid():     
            try:
                candidate_id = payload['candidate_id']
                action = payload['action']

                # candidate = get_user_model().objects.get(id=candidate_id)
                candidate = models.CandidatePosition.objects.filter(candidate=candidate_id).first()

                if action == "accepted":
                    candidate.application_status = "APPROVED"
                else:
                    candidate.application_status = "REJECTED"

                candidate.save()            
                return Response("success", status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(e)
                return Response({'details':'Error Approving Candidate'},status=status.HTTP_400_BAD_REQUEST)
        return Response({'details':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
