from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.conf import settings

from user_manager.models import ProfilePicture
from . import models
from user_manager.serializers import ProfilePictureSerializer, UsersSerializer
from app_manager import serializers as app_manager_serializers
from app_manager import models as app_manager_models
from user_manager.utils import user_util
from django.core.exceptions import ValidationError, ObjectDoesNotExist

import voting



# from user_manager import models as models

class SystemUsersSerializer(serializers.Serializer):
    UserId = serializers.CharField()
    email = serializers.CharField()
    firstname = serializers.CharField()
    lastname = serializers.CharField()


def getGenericSerializer(model_arg):
    class GenericSerializer(serializers.ModelSerializer):
        class Meta:
            model = model_arg
            fields = '__all__'
            # exclude = ('department', 'document')

    return GenericSerializer

def createGenericSerializer(model_arg,to_exclude):
    class GenericSerializer(serializers.ModelSerializer):
        class Meta:
            model = model_arg
            # fields = '__all__'
            exclude = to_exclude

    return GenericSerializer

class CreateCandidatePositionSerializer(serializers.Serializer):
    position = serializers.CharField()

class CandidateApprovalPositionSerializer(serializers.Serializer):
    candidate_id = serializers.CharField()
    action = serializers.CharField()

class FetchCandidatePositionSerializer(serializers.ModelSerializer):
    candidate = UsersSerializer()
    positionSerializer = getGenericSerializer(models.Positions)
    position = positionSerializer()
    profile_picture = serializers.SerializerMethodField('get_profile_picture')

    def get_profile_picture(self, obj):
        try:
            profile = ProfilePicture.objects.filter(user=obj.candidate_id, status=True).first()
            serializer = ProfilePictureSerializer(profile, many=False)
            return serializer.data
        except Exception as e:
            print(e)
            return []
    class Meta:
        model = models.CandidatePosition
        fields = '__all__'

class PostCommentsSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField('get_children')

    def get_children(self, obj):
        try:
            comment = models.PostCommentChildren.objects.filter(post=obj, status=True)
            commentSerializer = getGenericSerializer(models.PostCommentChildren)
            serializer = commentSerializer(comment, many=True)
            return serializer.data
        except Exception as e:
            print(e)
            return []

    class Meta:
        model = models.PostComments
        fields = '__all__'

class FetchPostSerializer(serializers.ModelSerializer):
    candidate = UsersSerializer()    
    post_image = serializers.SerializerMethodField('get_post_image')
    profile_picture = serializers.SerializerMethodField('get_profile_picture')
    post_comments = serializers.SerializerMethodField('get_post_comments')
    post_comment_children = serializers.SerializerMethodField('get_post_comment_children')
    post_likes = serializers.SerializerMethodField('get_post_likes')
    post_seen = serializers.SerializerMethodField('get_post_seen')

    def get_profile_picture(self, obj):
        try:
            profile = ProfilePicture.objects.filter(user=obj.candidate_id, status=True).first()
            serializer = ProfilePictureSerializer(profile, many=False)
            return serializer.data
        except Exception as e:
            print(e)
            return []

    def get_post_image(self, obj):
        try:
            image = models.PostImages.objects.filter(post=obj, status=True).first()
            ImageSerializer = getGenericSerializer(models.PostImages)
            serializer = ImageSerializer(image, many=False)
            return serializer.data
        except Exception as e:
            print(e)
            return []

    def get_post_comment(self, obj):
        try:
            comment = models.PostComments.objects.filter(post=obj, status=True)
            serializer = PostCommentsSerializer(comment, many=True)
            return serializer.data
        except Exception as e:
            print(e)
            return []
    
    def get_post_likes(self, obj):
        try:
            likes = models.PostLikes.objects.filter(post=obj, status=True).count()
            return likes
        except Exception as e:
            print(e)
            return 0

    def get_post_seen(self, obj):
        try:
            seen = models.PostSeen.objects.filter(post=obj, status=True).count()
            return seen
        except Exception as e:
            print(e)
            return 0

    class Meta:
        model = models.Posts
        fields = '__all__'

# class InnovationDetailsSerializer(serializers.ModelSerializer):
#     # innovation = InnovationSerializer()
#     industry = serializers.SerializerMethodField('get_industry')
#     development_stage = serializers.SerializerMethodField('get_development_stage')
#     # intellectual_property = app_manager_serializers.IntellectualPropertySerializer()
#     accreditation_bodies = serializers.SerializerMethodField('get_accreditation_bodies')
#     recognitions = serializers.SerializerMethodField('get_recognitions')
#     awards = serializers.SerializerMethodField('get_awards')
#     intellectual_property = serializers.SerializerMethodField('get_intellectual_property')
#     ip_document = serializers.SerializerMethodField('get_ip_document')
#     class Meta:
#         model = models.InnovationDetails
#         fields = '__all__'

#     def get_industry(self, obj):
#         try:
#             industry = app_manager_models.Industry.objects.get(id=obj.industry_id)
#             serializer = app_manager_serializers.IndustrySerializer(industry, many=False)
#             return serializer.data
#         except(ObjectDoesNotExist):
#             return []
#         except Exception as e:
#             print(e)
#             return []

#     def get_intellectual_property(self, obj):
#         try:
#             ip = app_manager_models.IntellectualProperty.objects.get(id=obj.intellectual_property_id)
#             serializer = app_manager_serializers.IntellectualPropertySerializer(ip, many=False)
#             return serializer.data
#         except(ObjectDoesNotExist):
#             return []
#         except Exception as e:
#             print(e)
#             return []

#     def get_ip_document(self, obj):
#         try:
#             ipdoc= models.InnovationDocument.objects.filter(innovation=obj.innovation_id)
#             serializer = InnovationDocumentSerializer(ipdoc, many=True)
#             return serializer.data
#         except(ObjectDoesNotExist):
#             return []
#         except Exception as e:
#             print(e)
#             return []

#     def get_development_stage(self, obj):
#         try:
#             development_stage = app_manager_models.DevelopmentStage.objects.get(id=obj.development_stage_id)
#             serializer = app_manager_serializers.DevelopmentStageSerializer(development_stage, many=False)
#             return serializer.data
#         except(ObjectDoesNotExist):
#             return []
#         except Exception as e:
#             print(e)
#             return []

#     def get_accreditation_bodies(self, obj):
#         try:
#             accreditation_bodies = models.AccreditationBody.objects.filter(innovation=obj.innovation_id)
#             serializer = GenericNameSerializer(accreditation_bodies, many=True)
#             return serializer.data
#         except Exception as e:
#             print(e)
#             return []

#     def get_recognitions(self, obj):
#         try:
#             recognitions = models.Recognitions.objects.filter(innovation=obj.innovation_id)
#             serializer = GenericNameSerializer(recognitions, many=True)
#             return serializer.data
#         except Exception as e:
#             print(e)
#             return []

#     def get_awards(self, obj):
#         try:
#             # print(obj.innovation_id)
#             awards = models.Awards.objects.filter(innovation=obj.innovation_id)
#             serializer = GenericNameSerializer(awards, many=True)
#             return serializer.data
#         except Exception as e:
#             print(e)
#             return []



# class FullInnovationSerializer(serializers.ModelSerializer):
#     creator = UsersSerializer()
#     details = serializers.SerializerMethodField(read_only=True)
#     information = serializers.SerializerMethodField(read_only=True)
#     support_services = serializers.SerializerMethodField(read_only=True)
#     other_support_services = serializers.SerializerMethodField()
#     social_links = serializers.SerializerMethodField(read_only=True)
#     group = serializers.SerializerMethodField(read_only=True)
#     jo_group = serializers.SerializerMethodField(read_only=True)
#     ie_group = serializers.SerializerMethodField(read_only=True)
#     sme_group = serializers.SerializerMethodField(read_only=True)
#     ee_group = serializers.SerializerMethodField(read_only=True)
#     review = serializers.SerializerMethodField(read_only=True)
#     evaluator_comments = serializers.SerializerMethodField(read_only=True)
#     im_reviews = serializers.SerializerMethodField()
#     all_im_reviews = serializers.SerializerMethodField()
#     fim_reviews = serializers.SerializerMethodField()
#     ie_reviews = serializers.SerializerMethodField()
#     sme_reviews = serializers.SerializerMethodField()
#     ee_reviews = serializers.SerializerMethodField()
#     is_evaluated = serializers.SerializerMethodField()
#     date_assigned = serializers.SerializerMethodField()
#     date_evaluated = serializers.SerializerMethodField()
#     evaluation_averages = serializers.SerializerMethodField()

#     class Meta:
#         model = models.Innovation
#         fields = '__all__'


#     def get_details(self, obj):
#         try:
#             details = models.InnovationDetails.objects.get(innovation=obj)
#             serializer = InnovationDetailsSerializer(details, many=False)
#             return serializer.data
#         except(ObjectDoesNotExist):
#             return []
#         except Exception as e:
#             print(e)
#             return []

#     def get_information(self, obj):
#         try:
#             information = models.InnovationInformation.objects.get(innovation=obj)
#             serializer = InnovationInformationSerializer(information, many=False)
#             return serializer.data
#         except(ObjectDoesNotExist):
#             return []
#         except Exception as e:
#             print(e)
#             return []

#     def get_support_services(self, obj):
#         support_services = models.InnovationSupportService.objects.filter(innovation=obj).order_by('service')
#         serializer = InnovationSupportServiceSerializer(support_services, many=True)
#         return serializer.data
    
#     def get_other_support_services(self, obj):
#         try:
#             support_services = models.OtherInnovationSupportService.objects.get(innovation=obj)
#             serializer = OtherInnovationSupportServiceSerializer(support_services, many=False)
#             return serializer.data
#         except(ObjectDoesNotExist):
#             return None
#         except Exception as e:
#             print(e)
#             return None

#     def get_social_links(self, obj):
#         try:
#             social_links = models.InnovationSocialLinks.objects.get(innovation=obj)
#             serializer = InnovationSocialLinksSerializer(social_links, many=False)
#             return serializer.data
#         except(ObjectDoesNotExist):
#             return []
#         except Exception as e:
#             print(e)
#             return []

#     def get_date_assigned(self, obj):
#         try:
#             try:
#                 jo = models.Group.objects.get(innovation=obj, role='JUNIOR_OFFICER').date_created
#             except:
#                 jo = ''
#             try:
#                 ie = models.Group.objects.get(innovation=obj, role='INTERNAL_EVALUATOR').date_created
#             except:
#                 ie = ''
#             try:
#                 sme = models.Group.objects.get(innovation=obj, role='SUBJECT_MATTER_EVALUATOR').date_created
#             except:
#                 sme = ''
#             try:
#                 ee = models.Group.objects.get(innovation=obj, role='EXTERNAL_EVALUATOR').date_created
#             except:
#                 ee = ''

#             date_assigned = {
#                 "jo":jo,
#                 "ie":ie,
#                 "sme":sme,
#                 "ee":ee,
#             }
#             return date_assigned
#         except(ObjectDoesNotExist):
#             return []
#         except Exception as e:
#             print(e)
#             return []
    
#     def get_group(self, obj):
#         try:
#             group = models.Group.objects.get(innovation=obj, status=True)
#             serializer = GroupSerializer(group, many=False)
#             return serializer.data
#         except(ObjectDoesNotExist):
#             return []
#         except Exception as e:
#             print(e)
#             return []

#     def get_jo_group(self, obj):
#         try:
#             group = models.Group.objects.get(innovation=obj, status=True, role='JUNIOR_OFFICER')
#             serializer = GroupSerializer(group, many=False)
#             return serializer.data
#         except(ObjectDoesNotExist):
#             return []
#         except Exception as e:
#             print(e)
#             return []

#     def get_ie_group(self, obj):
#         try:
#             group = models.Group.objects.get(innovation=obj, status=True, role='INTERNAL_EVALUATOR')
#             serializer = GroupSerializer(group, many=False)
#             return serializer.data
#         except(ObjectDoesNotExist):
#             return []
#         except Exception as e:
#             print(e)
#             return []

#     def get_sme_group(self, obj):
#         try:
#             group = models.Group.objects.get(innovation=obj, status=True, role='SUBJECT_MATTER_EVALUATOR')
#             serializer = GroupSerializer(group, many=False)
#             return serializer.data
#         except(ObjectDoesNotExist):
#             return []
#         except Exception as e:
#             print(e)
#             return []

#     def get_ee_group(self, obj):
#         try:
#             group = models.Group.objects.get(innovation=obj, status=True, role='EXTERNAL_EVALUATOR')
#             serializer = GroupSerializer(group, many=False)
#             return serializer.data
#         except(ObjectDoesNotExist):
#             return []
#         except Exception as e:
#             print(e)
#             return []

#     def get_review(self, obj):
#         try:
#             group = models.InnovationReview.objects.filter(innovation=obj.id).order_by('-date_created')
#             serializer = ReviewSerializer(group, many=True)
#             return serializer.data
#         except Exception as e:
#             print(e)
#             return []

#     def get_evaluator_comments(self, obj):
#         try:
#             current_lead = models.FinalEvaluatorsComment.objects.filter(innovation=obj.id,stage=obj.stage).order_by('-date_created')
#             serializer = FinalEvaluatorsCommentSerializer(current_lead, many=True)
#             current_lead = serializer.data

#             general = models.FinalEvaluatorsComment.objects.filter(innovation=obj.id).order_by('-date_created')
#             serializer = FinalEvaluatorsCommentSerializer(general, many=True)
#             general = serializer.data

#             info = {
#                 "current_lead" : current_lead,
#                 "general" : general,
#             }
#             return info
#         except Exception as e:
#             print(e)
#             return []

#     def get_evaluation_averages(self,obj):
#         try:
#             ie_average = 0     
#             try:       
#                 ie_reviews = self.get_ie_reviews(obj)
#                 for review in ie_reviews:
#                     ie_average += dict(review)['total_score']
#                 ie_average /= len(ie_reviews)
#                 ie_average = round(ie_average, 2)
#             except Exception as e:
#                 pass
            
#             ee_average = 0
#             try:
#                 ee_reviews = self.get_ee_reviews(obj)
#                 for review in ee_reviews:
#                     ee_average += dict(review)['total_score']
#                 ee_average /= len(ee_reviews)
#                 ee_average = round(ee_average, 2)
#             except Exception as e:
#                 pass

#             sme_average = 0
#             try:
#                 sme_reviews = self.get_sme_reviews(obj)
#                 for review in sme_reviews:
#                     sme_average += dict(review)['total_score']
#                 sme_average /= len(sme_reviews)
#                 sme_average = round(sme_average, 2)
#             except Exception as e:
#                 pass

#             info = {
#                 "ie_average" : ie_average,
#                 "ee_average" : ee_average,
#                 "sme_average" : sme_average
#             }
#             return info
#         except Exception as e:
#             print(e)

    
#     def get_im_reviews(self, obj):
#         try:
#             details = models.InnovationManagerReview.objects.get(innovation=obj.id,status=True)
#             serializer = InnovationManagerReviewSerializer(details, many=False)
#             return serializer.data
#         except(ObjectDoesNotExist):
#             return []
#         except Exception as e:
#             print(e)
#             return []

#     def get_all_im_reviews(self, obj):
#         try:
#             details = models.InnovationManagerReview.objects.filter(innovation=obj.id)
#             serializer = InnovationManagerReviewSerializer(details, many=True)
#             return serializer.data
#         except(ObjectDoesNotExist):
#             return []
#         except Exception as e:
#             print(e)
#             return []

#     def get_fim_reviews(self, obj):
#         try:
#             details = models.FinalInnovationManagerReview.objects.filter(innovation=obj.id, status=True).order_by('-date_created')
#             serializer = ReviewSerializer(details, many=True)
#             return serializer.data
#         except(ObjectDoesNotExist):
#             return []
#         except Exception as e:
#             print(e)
#             return []
    
#     def get_ie_reviews(self, obj):
#         try:
#             details = models.Evaluation.objects.filter(innovation=obj.id,role='INTERNAL_EVALUATOR').order_by('-date_created')
#             serializer = CreateEvaluationSerializer(details, many=True)
#             return serializer.data
#         except Exception as e:
#             print(e)
#             return []
    
#     def get_sme_reviews(self, obj):
#         try:
#             details = models.Evaluation.objects.filter(innovation=obj.id,role='SUBJECT_MATTER_EVALUATOR').order_by('-date_created')
#             serializer = CreateEvaluationSerializer(details, many=True)
#             return serializer.data
#         except Exception as e:
#             print(e)
#             return []
    
#     def get_ee_reviews(self, obj):
#         try:
#             details = models.Evaluation.objects.filter(innovation=obj.id,role='EXTERNAL_EVALUATOR').order_by('-date_created')
#             serializer = CreateEvaluationSerializer(details, many=True)
#             return serializer.data
#         except Exception as e:
#             print(e)
#             return []
    
#     def get_is_evaluated(self, obj):
#         try:
#             user_id = None
#             roles = []
#             try:
#                 user_id = str(self.context["user_id"])
#                 roles = user_util.fetchusergroups(user_id)
#             except Exception as e:
#                 # print(e)
#                 pass

#             if 'JUNIOR_OFFICER' in roles:
#                 evaluated = models.InnovationReview.objects.filter(innovation=obj.id,reviewer=user_id).exists()
#             else:
#                 evaluated = models.Evaluation.objects.filter(innovation=obj.id,evaluator=user_id).exists()
#             return evaluated
#         except Exception as e:
#             print(e)
#             return False

#     def get_date_evaluated(self, obj):
#         try:
#             user_id = None
#             roles = []
#             try:
#                 user_id = str(self.context["user_id"])
#                 roles = user_util.fetchusergroups(user_id)
#             except Exception as e:
#                 # print(e)
#                 pass

#             if 'JUNIOR_OFFICER' in roles:
#                 evaluated = models.InnovationReview.objects.filter(innovation=obj.id,reviewer=user_id)
#             else:
#                 evaluated = models.Evaluation.objects.filter(innovation=obj.id,evaluator=user_id)

#             if evaluated:
#                 evaluated = evaluated.first().date_created
#             else:
#                 evaluated = 'Pending'
#             return evaluated

#         except Exception as e:
#             print(e)
#             return False

# # 