from app_manager.models import Industry
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.conf import settings
from . import models
from user_manager.serializers import UsersSerializer
from app_manager import serializers as app_manager_serializers
from app_manager import models as app_manager_models
from user_manager.utils import user_util

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

class InnovationDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.InnovationDocument
        fields = '__all__'

class InnovationDetailsSerializer(serializers.ModelSerializer):
    # innovation = InnovationSerializer()
    industry = serializers.SerializerMethodField('get_industry')
    development_stage = serializers.SerializerMethodField('get_development_stage')
    # intellectual_property = app_manager_serializers.IntellectualPropertySerializer()
    accreditation_bodies = serializers.SerializerMethodField('get_accreditation_bodies')
    recognitions = serializers.SerializerMethodField('get_recognitions')
    awards = serializers.SerializerMethodField('get_awards')
    intellectual_property = serializers.SerializerMethodField('get_intellectual_property')
    ip_document = serializers.SerializerMethodField('get_ip_document')
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

    def get_intellectual_property(self, obj):
        try:
            ip = app_manager_models.IntellectualProperty.objects.get(id=obj.intellectual_property_id)
            serializer = app_manager_serializers.IntellectualPropertySerializer(ip, many=False)
            return serializer.data
        except Exception as e:
            print(e)
            return []

    def get_ip_document(self, obj):
        try:
            ipdoc= models.InnovationDocument.objects.filter(innovation=obj.innovation_id)
            serializer = InnovationDocumentSerializer(ipdoc, many=True)
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
    reviews = serializers.SerializerMethodField()
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

    def get_reviews(self, obj):
        try:
            details = models.InnovationManagerReview.objects.get(innovation=obj.id)
            serializer = InnovationManagerReviewSerializer(details, many=False)
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
    jo_group = serializers.SerializerMethodField(read_only=True)
    ie_group = serializers.SerializerMethodField(read_only=True)
    sme_group = serializers.SerializerMethodField(read_only=True)
    ee_group = serializers.SerializerMethodField(read_only=True)
    review = serializers.SerializerMethodField(read_only=True)
    evaluator_comments = serializers.SerializerMethodField(read_only=True)
    im_reviews = serializers.SerializerMethodField()
    fim_reviews = serializers.SerializerMethodField()
    ie_reviews = serializers.SerializerMethodField()
    sme_reviews = serializers.SerializerMethodField()
    ee_reviews = serializers.SerializerMethodField()
    is_evaluated = serializers.SerializerMethodField()
    date_assigned = serializers.SerializerMethodField()
    date_evaluated = serializers.SerializerMethodField()

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

    def get_date_assigned(self, obj):
        try:
            try:
                jo = models.Group.objects.get(innovation=obj, role='JUNIOR_OFFICER').date_created
            except:
                jo = ''
            try:
                ie = models.Group.objects.get(innovation=obj, role='INTERNAL_EVALUATOR').date_created
            except:
                ie = ''
            try:
                sme = models.Group.objects.get(innovation=obj, role='SUBJECT_MATTER_EVALUATOR').date_created
            except:
                sme = ''
            try:
                ee = models.Group.objects.get(innovation=obj, role='EXTERNAL_EVALUATOR').date_created
            except:
                ee = ''

            date_assigned = {
                "jo":jo,
                "ie":ie,
                "sme":sme,
                "ee":ee,
            }
            return date_assigned
        except Exception as e:
            print(e)
            return []
    
    def get_group(self, obj):
        try:
            group = models.Group.objects.get(innovation=obj, status=True)
            serializer = GroupSerializer(group, many=False)
            return serializer.data
        except Exception as e:
            print(e)
            return []

    def get_jo_group(self, obj):
        try:
            group = models.Group.objects.get(innovation=obj, status=True, role='JUNIOR_OFFICER')
            serializer = GroupSerializer(group, many=False)
            return serializer.data
        except Exception as e:
            print(e)
            return []

    def get_ie_group(self, obj):
        try:
            group = models.Group.objects.get(innovation=obj, status=True, role='INTERNAL_EVALUATOR')
            serializer = GroupSerializer(group, many=False)
            return serializer.data
        except Exception as e:
            print(e)
            return []

    def get_sme_group(self, obj):
        try:
            group = models.Group.objects.get(innovation=obj, status=True, role='SUBJECT_MATTER_EVALUATOR')
            serializer = GroupSerializer(group, many=False)
            return serializer.data
        except Exception as e:
            print(e)
            return []

    def get_ee_group(self, obj):
        try:
            group = models.Group.objects.get(innovation=obj, status=True, role='EXTERNAL_EVALUATOR')
            serializer = GroupSerializer(group, many=False)
            return serializer.data
        except Exception as e:
            print(e)
            return []

    def get_review(self, obj):
        try:
            group = models.InnovationReview.objects.filter(innovation=obj.id)
            serializer = ReviewSerializer(group, many=True)
            return serializer.data
        except Exception as e:
            print(e)
            return []

    def get_evaluator_comments(self, obj):
        try:
            current_lead = models.FinalEvaluatorsComment.objects.filter(innovation=obj.id,stage=obj.stage)
            serializer = FinalEvaluatorsCommentSerializer(current_lead, many=True)
            current_lead = serializer.data

            general = models.FinalEvaluatorsComment.objects.filter(innovation=obj.id)
            serializer = FinalEvaluatorsCommentSerializer(general, many=True)
            general = serializer.data

            info = {
                "current_lead" : current_lead,
                "general" : general,
            }
            return info
        except Exception as e:
            print(e)
            return []

    
    def get_im_reviews(self, obj):
        try:
            details = models.InnovationManagerReview.objects.get(innovation=obj.id,status=True)
            serializer = InnovationManagerReviewSerializer(details, many=False)
            return serializer.data
        except:
            return []

    def get_fim_reviews(self, obj):
        try:
            details = models.FinalInnovationManagerReview.objects.get(innovation=obj.id, status=True)
            serializer = ReviewSerializer(details, many=False)
            return serializer.data
        except Exception as e:
            print(e)
            return []
    
    def get_ie_reviews(self, obj):
        try:
            details = models.Evaluation.objects.filter(innovation=obj.id,role='INTERNAL_EVALUATOR')
            serializer = CreateEvaluationSerializer(details, many=True)
            return serializer.data
        except Exception as e:
            print(e)
            return []
    
    def get_sme_reviews(self, obj):
        try:
            details = models.Evaluation.objects.filter(innovation=obj.id,role='SUBJECT_MATTER_EVALUATOR')
            serializer = CreateEvaluationSerializer(details, many=True)
            return serializer.data
        except Exception as e:
            print(e)
            return []
    
    def get_ee_reviews(self, obj):
        try:
            details = models.Evaluation.objects.filter(innovation=obj.id,role='EXTERNAL_EVALUATOR')
            serializer = CreateEvaluationSerializer(details, many=True)
            return serializer.data
        except Exception as e:
            print(e)
            return []
    
    def get_is_evaluated(self, obj):
        try:
            user_id = None
            roles = []
            try:
                user_id = str(self.context["user_id"])
                roles = user_util.fetchusergroups(user_id)
            except Exception as e:
                print(e)
            if 'JUNIOR_OFFICER' in roles:
                evaluated = models.InnovationReview.objects.filter(innovation=obj.id,reviewer=user_id).exists()
            else:
                evaluated = models.Evaluation.objects.filter(innovation=obj.id,evaluator=user_id).exists()
            return evaluated
        except Exception as e:
            print(e)
            return False

    def get_date_evaluated(self, obj):
        try:
            user_id = None
            roles = []
            try:
                user_id = str(self.context["user_id"])
                roles = user_util.fetchusergroups(user_id)
            except Exception as e:
                print(e)
            if 'JUNIOR_OFFICER' in roles:
                evaluated = models.InnovationReview.objects.filter(innovation=obj.id,reviewer=user_id)
            else:
                evaluated = models.Evaluation.objects.filter(innovation=obj.id,evaluator=user_id)

            if evaluated:
                evaluated = evaluated.first().date_created
            else:
                evaluated = 'Pending'
            return evaluated

        except Exception as e:
            print(e)
            return False

class CreateEvaluationSerializer(serializers.ModelSerializer):  
    evaluator = UsersSerializer()
    class Meta:
        model = models.Evaluation
        fields = '__all__'
        # exclude = ('status', 'date_created')

class CustomCreateEvaluationSerializer(serializers.Serializer):
    innovation = serializers.CharField()
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

class CreateAssignmentResponseSerializer(serializers.Serializer):
    assignment_id = serializers.CharField()
    response = serializers.CharField()    

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

class FinalEvaluatorsCommentSerializer(serializers.ModelSerializer):  
    # innovation = InnovationSerializer()
    reviewer = UsersSerializer()
    class Meta:
        model = models.FinalEvaluatorsComment
        fields = '__all__'

class InnovationManagerReviewSerializer(serializers.ModelSerializer):  
    # innovation = InnovationSerializer()
    reviewer = UsersSerializer()
    class Meta:
        model = models.InnovationManagerReview
        fields = '__all__'


class CreateInnovationManagerReviewSerializer(serializers.Serializer):
    innovation = serializers.CharField()
    review = serializers.JSONField()


class NotificationsSerializer(serializers.ModelSerializer):  
    # innovation = InnovationSerializer()
    recipient = UsersSerializer()
    sender = UsersSerializer()
    class Meta:
        model = models.Notifications
        fields = '__all__'
