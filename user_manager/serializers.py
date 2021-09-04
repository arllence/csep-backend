import requests
from rest_framework import serializers
from django.contrib.auth import get_user_model
# from edms.models import DocumentActivity
from django.contrib.auth.models import Group
from django.conf import settings
from user_manager import models as models


class UserDetailSerializer(serializers.Serializer):
    username = serializers.CharField()
    id_number = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()


class SystemUsersSerializer(serializers.Serializer):
    UserId = serializers.CharField()
    email = serializers.CharField()
    firstname = serializers.CharField()
    lastname = serializers.CharField()


class PasswordChangeSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()
    current_password = serializers.CharField()


class GroupSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()


class UserIdSerializer(serializers.Serializer):
    user_id = serializers.CharField()


class DepartmentSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    keyword = serializers.CharField()


class UsersSerializer(serializers.ModelSerializer):
    id = serializers.CharField()
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    is_active = serializers.CharField()
    is_suspended = serializers.CharField()
    user_groups = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = get_user_model()
        fields = [
            'id', 'email', 'first_name', 'last_name', 'is_active', 'is_suspended','user_groups','date_created'
        ]

    def get_user_groups(self, obj):
        current_user = obj
        allgroups = Group.objects.filter(user=current_user)
        serializer = GroupSerializer(allgroups, many=True)
        return serializer.data


class SwapUserDepartmentSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    department_id = serializers.CharField()


class RoleSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()

class SkillsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Skills
        fields = '__all__'

class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProfilePicture
        fields = '__all__'

class ProfileInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserInfo
        fields = '__all__'


class CreateUserSerializer(serializers.Serializer):
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    # phone_number = serializers.CharField()
    register_as = serializers.CharField()
    # gender = serializers.CharField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()
    hear_about_us = serializers.CharField()
    newsletter = serializers.BooleanField()
    accepted_terms = serializers.BooleanField()

class CreateProfileSerializer(serializers.Serializer):
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone = serializers.CharField()
    age_group = serializers.CharField()
    gender = serializers.CharField()
    disability = serializers.CharField()
    country = serializers.CharField()
    bio = serializers.CharField()
    state = serializers.CharField()
    city = serializers.CharField()
    address = serializers.CharField()
    postal = serializers.CharField()
    level_of_education = serializers.CharField()
    employment = serializers.CharField()
    skills = serializers.ListField()


class UserProfileSerializer(serializers.Serializer):
    user = serializers.SerializerMethodField('get_user')
    profile_info = serializers.SerializerMethodField('get_profile_info')
    skills = serializers.SerializerMethodField('get_skills')
    profile_picture = serializers.SerializerMethodField('get_profile_picture')

    def get_profile_info(self, obj):
        current_user = obj
        profile = models.UserInfo.objects.get(user=current_user)
        serializer = ProfileInfoSerializer(profile, many=False)
        return serializer.data
    
    def get_profile_picture(self, obj):
        current_user = obj
        profile = models.ProfilePicture.objects.filter(user=current_user, status=True)
        serializer = ProfilePictureSerializer(profile[0], many=False)
        return serializer.data

    def get_skills(self, obj):
        current_user = obj
        skills = models.Skills.objects.filter(user=current_user)
        serializer = SkillsSerializer(skills, many=True)
        return serializer.data

    def get_user(self, obj):
        current_user = obj
        user = get_user_model().objects.get(id=current_user.id)
        serializer = UsersSerializer(user, many=False)
        return serializer.data


class SuspendUserSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    remarks = serializers.CharField()

class AccountActivitySerializer(serializers.Serializer):
    id = serializers.CharField()
    activity = serializers.CharField()

class OtpSerializer(serializers.Serializer):
    otp = serializers.CharField()
    email = serializers.CharField()

class ResendOtpSerializer(serializers.Serializer):
    email = serializers.CharField()


# class AccountActivityDetailSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DocumentActivity()
#         fields = '__all__'

class AccountActivityDetailSerializer(serializers.ModelSerializer):
    id = serializers.CharField()
    document = serializers.SerializerMethodField(read_only=True)
    user = serializers.SerializerMethodField(read_only=True)
    document_status= serializers.CharField()
    action_time = serializers.DateTimeField()

class EditUserSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    id_number = serializers.CharField()
    account_id = serializers.CharField()


class ManageRoleSerializer(serializers.Serializer):
    role_id = serializers.ListField(required=True)
    account_id = serializers.CharField()