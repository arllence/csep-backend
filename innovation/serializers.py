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

class GenericNameSerializer(serializers.Serializer):
    name = serializers.CharField()

class InnovationDetailsSerializer(serializers.ModelSerializer):
    # innovation = InnovationSerializer()
    industry = serializers.SerializerMethodField('get_industry')
    development_stage = serializers.SerializerMethodField('get_development_stage')
    # intellectual_property = app_manager_serializers.IntellectualPropertySerializer()
    accreditation_bodies = serializers.SerializerMethodField('get_accreditation_bodies')
    recognitions = serializers.SerializerMethodField('get_recognitions')
    awards = serializers.SerializerMethodField('get_awards')
    class Meta:
        model = models.InnovationDetails
        fields = '__all__'

    def get_industry(self, obj):
        try:
            industry = app_manager_models.Industry.objects.get(id=obj.industry_id)
            serializer = app_manager_serializers.IndustrySerializer(industry, many=False)
            return serializer.data
        except Exception as e:
            print(e)
            return []

    def get_development_stage(self, obj):
        try:
            development_stage = app_manager_models.DevelopmentStage.objects.get(id=obj.development_stage_id)
            serializer = app_manager_serializers.DevelopmentStageSerializer(development_stage, many=False)
            return serializer.data
        except Exception as e:
            print(e)
            return []

    def get_accreditation_bodies(self, obj):
        try:
            accreditation_bodies = models.AccreditationBody.objects.filter(innovation=obj.innovation_id)
            serializer = GenericNameSerializer(accreditation_bodies, many=True)
            return serializer.data
        except Exception as e:
            print(e)
            return []

    def get_recognitions(self, obj):
        try:
            recognitions = models.Recognitions.objects.filter(innovation=obj.innovation_id)
            serializer = GenericNameSerializer(recognitions, many=True)
            return serializer.data
        except Exception as e:
            print(e)
            return []

    def get_awards(self, obj):
        try:
            print(obj.innovation_id)
            awards = models.Awards.objects.filter(innovation=obj.innovation_id)
            serializer = GenericNameSerializer(awards, many=True)
            return serializer.data
        except Exception as e:
            print(e)
            return []

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
    other_industry = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    is_pitched_before = serializers.CharField()
    has_won_awards = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    awards = serializers.ListField(required=False,  allow_null=True,allow_empty=True, min_length=0)
    recognitions = serializers.ListField(required=False, allow_null=True, allow_empty=True, min_length=0)
    require_accreditation = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    accreditation_bodies = serializers.ListField(required=False, allow_null=True, allow_empty=True, min_length=0)
    hub_affiliation = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    hub_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    other_hub_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    


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
    group = serializers.SerializerMethodField(read_only=True)
    review = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Innovation
        fields = '__all__'


    def get_details(self, obj):
        try:
            details = models.InnovationDetails.objects.get(innovation=obj)
            serializer = InnovationDetailsSerializer(details, many=False)
            return serializer.data
        except Exception as e:
            print(e)
            return []

    def get_information(self, obj):
        try:
            information = models.InnovationInformation.objects.get(innovation=obj)
            serializer = InnovationInformationSerializer(information, many=False)
            return serializer.data
        except Exception as e:
            print(e)
            return []

    def get_support_services(self, obj):
        support_services = models.InnovationSupportService.objects.filter(innovation=obj)
        serializer = InnovationSupportServiceSerializer(support_services, many=True)
        return serializer.data

    def get_social_links(self, obj):
        try:
            social_links = models.InnovationSocialLinks.objects.get(innovation=obj)
            serializer = InnovationSocialLinksSerializer(social_links, many=False)
            return serializer.data
        except Exception as e:
            print(e)
            return []
    
    def get_group(self, obj):
        try:
            group = models.Group.objects.get(innovation=obj)
            serializer = GroupSerializer(group, many=False)
            return serializer.data
        except Exception as e:
            print(e)
            return []

    def get_review(self, obj):
        try:
            group = models.InnovationReview.objects.get(innovation=obj)
            serializer = ReviewSerializer(group, many=False)
            return serializer.data
        except Exception as e:
            print(e)
            return []

class CreateEvaluationSerializer(serializers.ModelSerializer):  
    class Meta:
        model = models.Evaluation
        fields = '__all__'
        # exclude = ('status', 'date_created')

class CreateNoteSerializer(serializers.Serializer):
    innovation = serializers.CharField()
    title = serializers.CharField()
    note = serializers.CharField()

class NoteSerializer(serializers.ModelSerializer):  
    innovation = InnovationSerializer()
    class Meta:
        model = models.Note
        fields = '__all__'

class DeleteNoteSerializer(serializers.Serializer):
    note_id = serializers.CharField()


class CreateAssignmentSerializer(serializers.Serializer):
    innovation = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    deadline = serializers.DateField()
    

class AssignmentSerializer(serializers.ModelSerializer):  
    innovation = InnovationSerializer()
    class Meta:
        model = models.Assignment
        fields = '__all__'

class DeleteAssignmentSerializer(serializers.Serializer):
    assignment_id = serializers.CharField()

class CreateGroupSerializer(serializers.Serializer):
    innovation = serializers.CharField()
    lead = serializers.CharField()
    role = serializers.CharField()
    assignees = serializers.ListField(min_length=1)

class GroupMemberSerializer(serializers.ModelSerializer):  
    # innovation = InnovationSerializer()
    member = UsersSerializer()
    class Meta:
        model = models.GroupMember
        fields = '__all__'
class GroupSerializer(serializers.ModelSerializer):  
    members = serializers.SerializerMethodField(read_only=True)

    def get_members(self, obj):
        try:
            members = models.GroupMember.objects.filter(group=obj)
            serializer = GroupMemberSerializer(members, many=True)
            return serializer.data
        except Exception as e:
            print(e)
            return []
    class Meta:
        model = models.Group
        fields = '__all__'

class CreateReviewSerializer(serializers.Serializer):
    innovation = serializers.CharField()
    action = serializers.CharField()
    review = serializers.CharField()

class ReviewSerializer(serializers.ModelSerializer):  
    # innovation = InnovationSerializer()
    reviewer = UsersSerializer()
    class Meta:
        model = models.InnovationReview
        fields = '__all__'