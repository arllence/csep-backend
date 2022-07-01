import json
import logging
from multiprocessing import context
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
            return Response({'details':'Error Deleting'},status=status.HTTP_400_BAD_REQUEST)


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


    # POSTS

    @action(methods=["POST"], detail=False, url_path="create-post", url_name="create-post")
    def create_post(self, request): 
        authenticated_user = request.user
        payload = request.data
        formfiles = request.FILES

        with transaction.atomic():
            sid = transaction.savepoint()
            post = payload.get('post')
            savedPost = models.Posts.objects.create(
                candidate=authenticated_user,
                post=post
            )
            
            if formfiles:
                
                for f in request.FILES.getlist('document'):
                    original_file_name = f.name

                    ext = original_file_name.split('.')[1].strip().lower()
                    exts = ['jpeg','jpg','png']

                    if ext not in exts:
                        transaction.savepoint_rollback(sid)
                        return Response({"details": "Please upload a picture!"}, status=status.HTTP_400_BAD_REQUEST)
                    
                    models.PostImages.objects.create(
                        post=savedPost,
                        image=f
                    )
            return Response("success", status=status.HTTP_200_OK)


    @action(methods=["POST"], detail=False, url_path="create-comment", url_name="create-comment")
    def create_comment(self, request): 
        authenticated_user = request.user
        payload = request.data
        print(payload)

        to_exclude = ('id','commentor','status','date_created')
        GenericSerializer = serializers.createGenericSerializer(models.PostComments,to_exclude)
        serializer = GenericSerializer(data=payload, many=False) 

        if serializer.is_valid():
            with transaction.atomic():

                comment = payload.get('comment')
                post_id = payload.get('post')

                post = models.Posts.objects.get(id=post_id)

                models.PostComments.objects.create(
                    post=post,
                    comment=comment,
                    commentor=authenticated_user
                )

                return Response("success", status=status.HTTP_200_OK)
        return Response({'details':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["POST"], detail=False, url_path="create-comment-child", url_name="create-comment-child")
    def create_comment_child(self, request): 
        authenticated_user = request.user
        payload = request.data
        print(payload)

        to_exclude = ('id','commentor','status','date_created')
        GenericSerializer = serializers.createGenericSerializer(models.PostCommentChildren,to_exclude)
        serializer = GenericSerializer(data=payload, many=False) 

        if serializer.is_valid():
            with transaction.atomic():

                comment = payload.get('comment')
                child = payload.get('child')

                commentInstance = models.PostComments.objects.get(id=comment)

                models.PostCommentChildren.objects.create(
                    comment=commentInstance,
                    child=child,
                    commentor=authenticated_user
                )

                return Response("success", status=status.HTTP_200_OK)
        return Response({'details':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["POST"], detail=False, url_path="delete-post", url_name="delete-post")
    def delete_post(self, request):    
        request_id = request.query_params.get('request_id')        
        try:
            post = models.Posts.objects.get(id=request_id)
            post.status = False
            post.save()            
            return Response("success", status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response({'details':'Error deleting post'},status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=False, url_path="delete-comment", url_name="delete-comment")
    def delete_comment(self, request):    
        request_id = request.query_params.get('request_id')        
        try:
            comment = models.PostComments.objects.get(id=request_id)
            comment.status = False
            comment.save()            
            return Response("success", status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response({'details':'Error deleting comment'},status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=False, url_path="delete-comment-child", url_name="delete-comment-child")
    def delete_comment_child(self, request):    
        request_id = request.query_params.get('request_id')        
        try:
            comment = models.PostCommentChildren.objects.get(id=request_id)
            comment.status = False
            comment.save()            
            return Response("success", status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response({'details':'Error deleting comment'},status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["GET"], detail=False, url_path="fetch-posts", url_name="fetch-posts")
    def fetch_posts(self, request):
        try:
            posts = models.Posts.objects.all().order_by('date_created').exclude(status=False)

            serializer = serializers.FetchPostSerializer(posts, many=True,context={"user_id":request.user.id})   
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            logger.error(e)
            return Response({'details':'Error Fetching Posts'},status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["POST"], detail=False, url_path="create-like", url_name="create-like")
    def create_like(self, request): 
        authenticated_user = request.user
        payload = request.data

        with transaction.atomic():
            post_id = payload.get('post_id')
            if post_id is None:
                return Response({'details':'Error performing request'},status=status.HTTP_400_BAD_REQUEST)

            is_liked = models.PostLikes.objects.filter(post=post_id,liker=authenticated_user)
            if is_liked:
                post = is_liked.first()
                post.delete()
            else:
                post = models.Posts.objects.get(id=post_id)
                models.PostLikes.objects.create(
                    post=post,
                    liker=authenticated_user
                )
            return Response('success', status=status.HTTP_200_OK)



    @action(methods=["POST"], detail=False, url_path="create-seen", url_name="create-seen")
    def create_seen(self, request): 
        authenticated_user = request.user
        payload = request.data

        with transaction.atomic():
            post_id = payload.get('post_id')
            if post_id is None:
                return Response({'details':'Error performing request'},status=status.HTTP_400_BAD_REQUEST)

            is_seen = models.PostSeen.objects.filter(post=post_id,liker=authenticated_user).exists()
            if not is_seen:
                post = models.Posts.objects.get(id=post_id)
                models.PostSeen.objects.create(
                    post=post,
                    user=authenticated_user
                )
            return Response('success', status=status.HTTP_200_OK)



        

