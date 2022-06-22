
from . import models
from . import serializers 
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets, status
from django.contrib.auth import get_user_model



class AdminManagementViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,JSONParser)
    queryset = get_user_model().objects.all().order_by('id')
    serializer_class = serializers.SystemUsersSerializer
    search_fields = ['id', ]

    def get_queryset(self):
        return []

   



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