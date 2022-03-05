from django.contrib.auth import get_user_model
# from edms.permissions import system_permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from analytics import serializers
# from edms import models as edms_models
from django.db.models import Count, Q
from analytics.utils import dates
import json
from innovation import models as innovation_models
from user_manager import models as user_manager_models
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from datetime import datetime
date_class = dates.DateClass()


class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [
        IsAuthenticated]

    def get_queryset(self):
        return []

    @action(
        methods=["GET"],
        detail=False,
        url_path="list-innovators",
        url_name="list-innovators",
    )
    def list_innovators(self, request):
        selected_records = get_user_model().objects.filter(
            groups__name='INNOVATOR').order_by('first_name')
        records_data = serializers.UserSerializer(selected_records, many=True)
        return Response(records_data.data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=False,
        url_path="list-evaluators",
        url_name="list-evaluators",
    )
    def list_evaluators(self, request):
        selected_records = get_user_model().objects.filter(
            groups__name='EVALUATOR').order_by('first_name')
        records_data = serializers.UserSerializer(selected_records, many=True)
        return Response(records_data.data, status=status.HTTP_200_OK)

    
    @action(
        methods=["GET"],
        detail=False,
        url_path="list-investors",
        url_name="list-investors",
    )
    def list_investors(self, request):
        selected_records = get_user_model().objects.filter(
            groups__name='INVESTOR').order_by('first_name')
        records_data = serializers.UserSerializer(selected_records, many=True)
        return Response(records_data.data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=False,
        url_path="list-mentors",
        url_name="list-mentors",
    )
    def list_mentors(self, request):
        selected_records = get_user_model().objects.filter(
            groups__name='MENTOR').order_by('first_name')
        records_data = serializers.UserSerializer(selected_records, many=True)
        return Response(records_data.data, status=status.HTTP_200_OK)


    @action(
        methods=["GET"],
        detail=False,
        url_path="list-managers",
        url_name="list-managers",
    )
    def list_managers(self, request):
        selected_records = get_user_model().objects.filter(
            groups__name='MANAGER').order_by('first_name')
        records_data = serializers.UserSerializer(selected_records, many=True)
        return Response(records_data.data, status=status.HTTP_200_OK)



    @action(
        methods=["GET"],
        detail=False,
        url_path="list-partners",
        url_name="list-partners",
    )
    def list_partners(self, request):
        selected_records = get_user_model().objects.filter(
            groups__name='PARTNER').order_by('first_name')
        records_data = serializers.UserSerializer(selected_records, many=True)
        return Response(records_data.data, status=status.HTTP_200_OK)


    @action(
        methods=["GET"],
        detail=False,
        url_path="general-counts",
        url_name="general-counts",
    )
    def general_count(self, request):
        innovations = innovation_models.Innovation.objects.all().count()
        innovators = get_user_model().objects.filter(
            groups__name='INNOVATOR').count()
        evaluators = get_user_model().objects.filter(
            groups__name='EVALUATOR').count()
        investors = get_user_model().objects.filter(
            groups__name='INVESTOR').count()
        mentors = get_user_model().objects.filter(
            groups__name='MENTOR').count()
        managers = get_user_model().objects.filter(
            groups__name='MANAGER').count()
        partners = get_user_model().objects.filter(
            groups__name='PARTNER').count()

        series = [
            {"data": [innovations],"label":"Innovations"},
            {"data": [innovators],"label":"Innovators"},
            {"data": [evaluators],"label":"Evaluators"},
            {"data": [investors],"label":"Investors"},
            {"data": [mentors],"label":"Mentors"},
            {"data": [managers],"label":"Managers"},
            {"data": [partners],"label":"Partners"},
        ]
        info = {
            "innovations" : innovations,
            "innovators" : innovators,
            "evaluators" : evaluators,
            "investors" : investors,
            "mentors" : mentors,
            "managers" : managers,
            "partners" : partners,
            "series" : series
        }
        return Response(info, status=status.HTTP_200_OK)


    @action(
        methods=["GET"],
        detail=False,
        url_path="monthly-user-registration",
        url_name="monthly-user-registration",
    )
    def monthly_user_registration(self, request):
        year = request.query_params.get('year')
        if year is None:
            year = int(str(datetime.now().year))
        
        data = []
        
        for i in range(1,13):
            count = get_user_model().objects.filter(date_created__year=year,date_created__month=i).count()
            data.append(count)

        series = [{"data": data,"label":"Registered Users",}]

        info = {
            "series" : series,
        }
        return Response(info, status=status.HTTP_200_OK)


    @action(
        methods=["GET"],
        detail=False,
        url_path="user-by-gender",
        url_name="user-by-gender",
    )
    def user_by_gender(self, request):     

        male_count = user_manager_models.UserInfo.objects.filter(gender='Male').count()
        female_count = user_manager_models.UserInfo.objects.filter(gender='Female').count()

        series = [
            male_count,female_count
        ]

        info = {
            "series" : series,
        }
        return Response(info, status=status.HTTP_200_OK)


    @action(
        methods=["GET"],
        detail=False,
        url_path="junior-counts",
        url_name="junior-counts",
    )
    def junior_count(self, request):
        user = request.user
        role = 'JUNIOR_OFFICER'

        innovations = innovation_models.GroupMember.objects.filter(member=user, group__role=role).order_by('-date_created')

        total = innovations.count()
        completed =  0
        pending = 0

        for innovation in innovations:
            check = innovation_models.InnovationReview.objects.filter(innovation=innovation.group.innovation.id,reviewer=user).exists()
            
            if check:
                completed += 1
            else:
                pending += 1


        info = {
            "total" : total,
            "completed" : completed,
            "pending" : pending,
            "assigned" : pending,
        }
        return Response(info, status=status.HTTP_200_OK)
    

   
