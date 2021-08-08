import os
import uuid
import datetime
from uuid import uuid4
from django.db import models
from storage import smb_storage
from django.conf import settings
from .managers import UserManager
from django.contrib.auth.models import Group, PermissionsMixin
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

media_mode = settings.MAINMEDIA
smb_system_storage = smb_storage.SMBStorage()

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    # phone_number = models.CharField(max_length=50)
    # gender = models.CharField(max_length=50)
    register_as = models.CharField(max_length=50)
    hear_about_us = models.CharField(max_length=255, blank=True,null=True)
    accepted_terms = models.BooleanField(default=False)
    newsletter = models.BooleanField(default=False)
    verified_email = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_defaultpassword = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)
    last_password_reset = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)
    objects = UserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return str(self.email)

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    class Meta:
        db_table = "systemusers"


class UserInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_profile_info"
    )
    profile_picture = models.ImageField(upload_to='profile_images', blank=True)
    phone = models.CharField(max_length=50)
    id_number = models.CharField(max_length=50)
    gender = models.CharField(max_length=50)
    bio = models.TextField()
    age_group = models.CharField(max_length=100)
    disability = models.TextField()

    country = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    physical_address = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=100)

    education_level = models.CharField(max_length=100)
    employment_status = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True)

    
    class Meta:
        app_label = "user_manager"
        db_table = "user_info"

    def __str__(self):
        return str(self.id)


class ProfilePicture(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_profile_picture"
    )
    profile_picture = models.ImageField(upload_to='profile_images')
    original_file_name = models.CharField(max_length=100)
    status = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "user_manager"
        db_table = "profile_picture"

    def __str__(self):
        return str(self.profile_picture.url)

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_documents"
    )
    document = models.ImageField(upload_to='documents')
    original_file_name = models.CharField(max_length=100)
    status = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "user_manager"
        db_table = "documets"

    def __str__(self):
        return str(self.id)

class Skills(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_profile"
    )
    name = models.CharField(max_length=50)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "user_manager"
        db_table = "skills"

    def __str__(self):
        return str(self.name)


class CompletedProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_completed_profile"
    )
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "user_manager"
        db_table = "completed_profile"

    def __str__(self):
        return str(self.user.email)

class AccountActivity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        User, related_name="user_account_activity", on_delete=models.CASCADE
    )
    actor = models.ForeignKey(
        User, related_name="activity_actor", on_delete=models.CASCADE
    )
    activity = models.TextField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    action_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "user_manager"
        db_table = "account_activity"

    def __str__(self):
        return str(self.id)



class OtpCodes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        User, related_name="user_otp_code", on_delete=models.CASCADE
    )    
    otp = models.CharField(max_length=50)
    action_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "user_manager"
        db_table = "otp_codes"

    def __str__(self):
        return str(self.id)



