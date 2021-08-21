import innovation
import uuid
from django.db import models
from user_manager.models import User
from app_manager import models as app_manager_models



class Innovation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission_terms = models.BooleanField(default=False)
    creator = models.ForeignKey(
       User, on_delete=models.CASCADE, related_name="innovation_creator"
    )
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "innovation"
        db_table = "innovation"

    def __str__(self):
        return str(self.id)



class InnovationDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    innovation = models.ForeignKey(
       Innovation, on_delete=models.CASCADE, related_name="innovation_industry"
    )
    innovation_name = models.CharField(max_length=100)
    industry = models.ForeignKey(
        app_manager_models.Industry, on_delete=models.CASCADE, related_name="innovation_industry"
    )
    other_industry = models.CharField(max_length=100, blank=True, null=True)
    area_of_focus = models.CharField(max_length=100)
    development_stage = models.ForeignKey(
        app_manager_models.DevelopmentStage, on_delete=models.CASCADE, related_name="innovation_industry"
    )
    is_pitched_before = models.CharField(max_length=100)
    has_won_awards = models.CharField(max_length=100, blank=True, null=True)
    awards = models.CharField(max_length=100, blank=True, null=True)
    recognitions = models.CharField(max_length=100)
    require_accreditation = models.CharField(max_length=100, blank=True, null=True)
    accreditation_bodies = models.CharField(max_length=100, blank=True, null=True)
    hub_affiliation = models.CharField(max_length=100, blank=True, null=True)
    hub_name = models.CharField(max_length=100, blank=True, null=True)
    other_hub_name = models.CharField(max_length=100, blank=True, null=True)
    intellectual_property = models.ForeignKey(
        app_manager_models.IntellectualProperty, on_delete=models.CASCADE, related_name="innovation_industry"
    )
    date_created = models.DateTimeField(auto_now_add=True)


    class Meta:
        app_label = "innovation"
        db_table = "innovation_details"

    def __str__(self):
        return str(self.innovation_name)


class InnovationInformation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    innovation = models.ForeignKey(
       Innovation, on_delete=models.CASCADE, related_name="innovation_industry"
    )
    innovation_brief = models.TextField()
    problem_statement = models.TextField()
    background_research = models.TextField()
    target_customers = models.TextField()
    value_proposition = models.TextField()
    solution = models.TextField()
    how_it_works = models.TextField()
    impact = models.TextField()
    competitors = models.TextField()
    competitive_advantage = models.TextField()   
    date_created = models.DateTimeField(auto_now_add=True)


    class Meta:
        app_label = "innovation"
        db_table = "innovation_information"

    def __str__(self):
        return str(self.id)


class InnovationSocialLinks(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    innovation = models.ForeignKey(
       Innovation, on_delete=models.CASCADE, related_name="innovation_industry"
    )
    innovation_video = models.CharField(max_length=100)
    facebook = models.CharField(max_length=100, blank=True, null=True)
    twitter = models.CharField(max_length=100, blank=True, null=True)
    instagram = models.CharField(max_length=100, blank=True, null=True)
    linkedin = models.CharField(max_length=100, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "innovation"
        db_table = "innovation_social_links"

    def __str__(self):
        return str(self.id)


class InnovationSupportService(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    innovation = models.ForeignKey(
       Innovation, on_delete=models.CASCADE, related_name="innovation_industry"
    )
    service = models.ForeignKey(
        app_manager_models.SupportServices, on_delete=models.CASCADE, related_name="innovation_industry"
    )
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "innovation"
        db_table = "innovation_support_services"

    def __str__(self):
        return str(self.id)