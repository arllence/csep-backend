from binascii import Incomplete
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
import json, logging
from innovation import models as innovation_models
from user_manager import models as user_manager_models
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from datetime import datetime
from user_manager.utils import user_util
date_class = dates.DateClass()

# Get an instance of a logger
logger = logging.getLogger(__name__)

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
            Q(groups__name='EVALUATOR') |  Q(groups__name='INTERNAL_EVALUATOR') |  Q(groups__name='EXTERNAL_EVALUATOR') | Q(groups__name='SUBJECT_MATTER_EVALUATOR') |  Q(groups__name='CHIEF_EVALUATOR')).count()
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

        role = None
        roles = user_util.fetchusergroups(user.id)
        for item in roles:
            # print(item)
            if 'LEAD' not in item:
                if 'CHIEF' not in item:
                    role = item
                else:
                    is_chief_evaluator = True
                    role = 'EXTERNAL_EVALUATOR'
            else:
                # if item != 'LEAD_JUNIOR_OFFICER':
                is_lead = True

        
        innovations = innovation_models.GroupMember.objects.filter(member=user, group__role=role).order_by('-date_created')

        total = innovations.count()
        completed =  0
        pending = 0

        for innovation in innovations:
            if role == 'JUNIOR_OFFICER':
                check = innovation_models.InnovationReview.objects.filter(innovation=innovation.group.innovation.id,reviewer=user).exists()
            else:
                check = innovation_models.Evaluation.objects.filter(innovation=innovation.group.innovation.id,evaluator=user).exists()
            
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

    @action(methods=["GET"], detail=False, url_path="im-analytics", url_name="im-analytics")
    def get_im_analytics(self, request):
        user = request.user
        
        is_chief_evaluator = False
        is_lead_innovation_manager = False
        is_lead = False
        role = None

        roles = user_util.fetchusergroups(user.id)

        for item in roles:
            if item == 'LEAD_INNOVATION_MANAGER':
                is_lead_innovation_manager = True

        try:    
            if is_lead_innovation_manager:
                completed = innovation_models.Innovation.objects.filter(status='COMPLETED').count()
                approved = innovation_models.Innovation.objects.filter(status='APPROVED').count()
                dropped = innovation_models.Innovation.objects.filter(status='DROPPED').count()
                under_review = innovation_models.Innovation.objects.filter(status='UNDER_REVIEW').count()
                incomplete = innovation_models.Innovation.objects.filter(status='ONGOING').count()
                resubmitted = innovation_models.Innovation.objects.filter(status='RESUBMITTED').count()
                pending_resubmission = innovation_models.Innovation.objects.filter(status='RESUBMIT').count()

                info = {
                    "completed": completed,
                    "approved": approved,
                    "dropped": dropped,
                    "under_review": under_review,
                    "incomplete": incomplete,
                    "resubmitted": resubmitted,
                    "pending_resubmission": pending_resubmission,
                }
                
                return Response(info, status=status.HTTP_200_OK)
            else:
                return Response([], status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(e)
            return Response({'details':'Error Fetching Analytics'},status=status.HTTP_400_BAD_REQUEST)
    

   
