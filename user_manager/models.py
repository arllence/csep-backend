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
from PIL import Image


media_mode = settings.MAINMEDIA
smb_system_storage = smb_storage.SMBStorage()

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    registration_no = models.CharField(max_length=50, unique=True)
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

    USERNAME_FIELD = "registration_no"

    def __str__(self):
        return str(self.registration_no)

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
    phone = models.CharField(max_length=50, null=True, blank=True)
    gender = models.CharField(max_length=50)
    bio = models.TextField()
    age_group = models.CharField(max_length=100)
    disability = models.TextField()
    education_level = models.CharField(max_length=100, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    
    class Meta:
        app_label = "user_manager"
        db_table = "user_info"

    def __str__(self):
        return str(self.id)

class Education(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_education_profile"
    )
    institution_name = models.CharField(max_length=255)
    course_name = models.CharField(max_length=255, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "user_manager"
        db_table = "education"

    def __str__(self):
        return str(self.institution_name)


class Certification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_certifications"
    )
    name = models.CharField(max_length=255)
    expiration_date = models.CharField(max_length=50, null=True, blank=True)
    status = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "user_manager"
        db_table = "certifications"

    def __str__(self):
        return str(self.name)





class Hobby(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_hobbies"
    )
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "user_manager"
        db_table = "hobbies"

    def __str__(self):
        return str(self.name)

class ProfilePicture(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_profile_picture"
    )
    profile_picture = models.ImageField(upload_to='profile_images')
    original_file_name = models.CharField(max_length=100)
    status = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save()
        img = Image.open(self.profile_picture.path)
        # width, height = img.size  # Get dimensions
        size = (300,300)
        image = img.resize(size, Image.ANTIALIAS)
        image.save(self.profile_picture.path)

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
    document_type = models.CharField(max_length=200, blank=True, null=True)
    original_file_name = models.CharField(max_length=100)
    status = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "user_manager"
        db_table = "documents"

    def __str__(self):
        return str(self.id)


class Association(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_Associations"
    )
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    expiration = models.DateField(null=True, blank=True)
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="user_Documents", null=True, blank=True
    )

    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "user_manager"
        db_table = "associations"

    def __str__(self):
        return str(self.name)       

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



