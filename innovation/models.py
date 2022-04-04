import innovation
import uuid
from django.db import models
from user_manager.models import User
from app_manager import models as app_manager_models




class Innovation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission_terms = models.BooleanField(default=False)
    status = models.CharField(max_length=255, default="ONGOING")
    creator = models.ForeignKey(
       User, on_delete=models.CASCADE, related_name="innovation_creator"
    )
    stage = models.CharField(max_length=5, default="I")
    edit = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "innovation"
        db_table = "innovation"

    def __str__(self):
        return str(self.id)

class InnovationDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    innovation = models.ForeignKey(
       Innovation, on_delete=models.CASCADE, related_name="innovation_documents"
    )
    document = models.ImageField(upload_to='documents')
    original_file_name = models.CharField(max_length=255)
    title = models.CharField(max_length=255, blank=True, null=True)
    status = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    class Meta:
        app_label = "innovation"
        db_table = "innovation_documents"

    def __str__(self):
        return str(self.title)

class InnovationDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    innovation = models.ForeignKey(
       Innovation, on_delete=models.CASCADE, related_name="innovation_industry"
    )
    innovation_name = models.CharField(max_length=255)
    industry = models.ForeignKey(
        app_manager_models.Industry, on_delete=models.CASCADE, related_name="innovation_industry"
    )
    other_industry = models.CharField(max_length=255, blank=True, null=True)
    area_of_focus = models.CharField(max_length=255)
    development_stage = models.ForeignKey(
        app_manager_models.DevelopmentStage, on_delete=models.CASCADE, related_name="innovation_development_stage"
    )
    is_pitched_before = models.CharField(max_length=255)
    has_won_awards = models.CharField(max_length=255, blank=True, null=True)
    # awards = models.CharField(max_length=255, blank=True, null=True)
    # recognitions = models.CharField(max_length=255, default=None)
    require_accreditation = models.CharField(max_length=255, blank=True, null=True)
    # accreditation_bodies = models.CharField(max_length=255, blank=True, null=True)
    hub_affiliation = models.CharField(max_length=255, blank=True, null=True)
    hub_name = models.CharField(max_length=255, blank=True, null=True)
    other_hub_name = models.CharField(max_length=255, blank=True, null=True)
    intellectual_property = models.ForeignKey(
        app_manager_models.IntellectualProperty, on_delete=models.CASCADE, related_name="innovation_intellectual_property", default=None,  blank=True, null=True
    )
    date_created = models.DateTimeField(auto_now_add=True)


    class Meta:
        app_label = "innovation"
        db_table = "innovation_details"

    def __str__(self):
        return str(self.innovation_name)

class PendingFinalReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    innovation = models.ForeignKey(
       Innovation, on_delete=models.CASCADE, related_name="innovation_pending_final_report"
    )
    status = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    class Meta:
        app_label = "innovation"
        db_table = "pending_final_report"

    def __str__(self):
        return str(self.innovation.id)

class AccreditationBody(models.Model):
    innovation = models.ForeignKey(
       Innovation, on_delete=models.CASCADE, related_name="accreditation_bodies"
    )
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)    
    date_created = models.DateTimeField(auto_now_add=True)
    class Meta:
        app_label = "innovation"
        db_table = "accreditation_bodies"

    def __str__(self):
        return str(self.name)


class Recognitions(models.Model):
    innovation = models.ForeignKey(
       Innovation, on_delete=models.CASCADE, related_name="recognitions"
    )
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)    
    date_created = models.DateTimeField(auto_now_add=True)
    class Meta:
        app_label = "innovation"
        db_table = "recognitions"

    def __str__(self):
        return str(self.name)

class Awards(models.Model):
    innovation = models.ForeignKey(
       Innovation, on_delete=models.CASCADE, related_name="awards"
    )
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)    
    date_created = models.DateTimeField(auto_now_add=True)
    class Meta:
        app_label = "innovation"
        db_table = "awards"

    def __str__(self):
        return str(self.name)

class InnovationInformation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    innovation = models.ForeignKey(
       Innovation, on_delete=models.CASCADE, related_name="innovation_information"
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
       Innovation, on_delete=models.CASCADE, related_name="innovation_social_links"
    )
    innovation_video = models.CharField(max_length=255)
    website = models.CharField(max_length=255, blank=True, null=True)
    facebook = models.CharField(max_length=255, blank=True, null=True)
    twitter = models.CharField(max_length=255, blank=True, null=True)
    instagram = models.CharField(max_length=255, blank=True, null=True)
    linkedin = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "innovation"
        db_table = "innovation_social_links"

    def __str__(self):
        return str(self.id)


class InnovationSupportService(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    innovation = models.ForeignKey(
       Innovation, on_delete=models.CASCADE, related_name="innovation_support_services"
    )
    service = models.ForeignKey(
        app_manager_models.SupportServices, on_delete=models.CASCADE, related_name="innovation_service"
    )
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "innovation"
        db_table = "innovation_support_services"

    def __str__(self):
        return str(self.id)


class OtherInnovationSupportService(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    innovation = models.ForeignKey(
       Innovation, on_delete=models.CASCADE, related_name="otehr_innovation_support_services"
    )
    service = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "innovation"
        db_table = "other_innovation_support_services"

    def __str__(self):
        return str(self.id)


class Evaluation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    innovation = models.ForeignKey(
       Innovation, on_delete=models.CASCADE, related_name="evaluation"
    )
    evaluator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="evaluation_creator", blank=True, null=True # TODO: remove is nullable
    )
    role = models.CharField(max_length=100, blank=True, null=True)
    innovation_brief_score = models.IntegerField()
    innovation_brief_observation = models.TextField()
    innovation_brief_comment = models.TextField()
    problem_statement_score = models.IntegerField()
    problem_statement_observation = models.TextField()
    problem_statement_comment = models.TextField()
    solution_score = models.IntegerField()
    solution_observation = models.TextField()
    solution_comment = models.TextField()
    how_it_works_score = models.IntegerField()
    how_it_works_observation = models.TextField()
    how_it_works_comment = models.TextField()
    target_customers_score = models.IntegerField()
    target_customers_observation = models.TextField()
    target_customers_comment = models.TextField()
    value_proposition_score = models.IntegerField()
    value_proposition_observation = models.TextField()
    value_proposition_comment = models.TextField()
    competitive_advantage_score = models.IntegerField()
    competitive_advantage_observation = models.TextField()
    competitive_advantage_comment = models.TextField()
    background_research_score = models.IntegerField()
    background_research_observation = models.TextField()
    background_research_comment = models.TextField()
    impact_score = models.IntegerField()
    impact_observation = models.TextField()
    impact_comment = models.TextField()
    competitors_score = models.TextField()
    competitors_observation = models.TextField()
    competitors_comment = models.TextField()
    final_observation = models.TextField()
    final_comment = models.TextField()
    total_score = models.IntegerField()
    outcome = models.CharField(max_length=100, default=None)
    status = models.BooleanField(default=True)    
    date_created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        total_scores = self.innovation_brief_score + self.problem_statement_score + self.solution_score + self.how_it_works_score + self.target_customers_score + self.value_proposition_score + self.competitive_advantage_score + self.background_research_score + self.impact_score + self.competitors_score
        self.total_score = total_scores
        super().save(*args, **kwargs)
    class Meta:
        app_label = "innovation"
        db_table = "evaluations"

    def __str__(self):
        return str(self.name)


class Note(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    innovation = models.ForeignKey(
       Innovation, on_delete=models.CASCADE, related_name="notes"
    )
    created_by =models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="note_creator"
    )
    title = models.CharField(max_length=255)
    note = models.TextField()
    status = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "innovation"
        db_table = "notes"

    def __str__(self):
        return str(self.id)


class Assignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    innovation = models.ForeignKey(
       Innovation, on_delete=models.CASCADE, related_name="assignments"
    )
    created_by =models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="assignment_creator"
    )
    title = models.CharField(max_length=255)
    deadline = models.DateField()
    file = models.FileField(upload_to='documents', blank=True, null=True)
    assignment_status = models.CharField(max_length=100, default="PENDING")
    description = models.TextField()
    status = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "innovation"
        db_table = "assignments"

    def __str__(self):
        return str(self.id)

class AssignmentResponse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.ForeignKey(
       Assignment, on_delete=models.CASCADE, related_name="assignment_response"
    )
    file = models.FileField(upload_to='documents', blank=True, null=True)
    assignment_status = models.CharField(max_length=100, default="SUBMITTED")
    response = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "innovation"
        db_table = "assignment_response"

    def __str__(self):
        return str(self.id)

class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    innovation = models.ForeignKey(
       Innovation, on_delete=models.CASCADE, related_name="groups"
    )
    creator =models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="creator", blank=True, null=True
    )
    role = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "groups"

    def __str__(self):
        return str(self.id)

class GroupMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(
       Group, on_delete=models.CASCADE, related_name="groups"
    )
    member =models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="member"
    )
    is_lead = models.BooleanField(default=False)
    status = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "group_members"

    def __str__(self):
        return str(self.id)



class InnovationReview(models.Model): # TODO: Rename this model to JuniorInnovationReview
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    innovation = models.ForeignKey(
       Innovation, on_delete=models.CASCADE, related_name="reviews"
    )
    reviewer =models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="review_creator"
    )
    review = models.TextField()
    action = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    is_seen = models.BooleanField(default=False)
    is_lead = models.BooleanField(default=False)
    is_final = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "innovation_reviews"

    def __str__(self):
        return str(self.id)


class FinalEvaluatorsComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    innovation = models.ForeignKey(
       Innovation, on_delete=models.CASCADE, related_name="innovation_reviews"
    )
    reviewer =models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comment_creator"
    )
    review = models.TextField()
    action = models.CharField(max_length=255)
    stage = models.CharField(max_length=50, blank=True, null=True)
    status = models.BooleanField(default=True)
    is_seen = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "final_evaluators_comments"

    def __str__(self):
        return str(self.id)


class InnovationManagerReview(models.Model): 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    innovation = models.ForeignKey(
       Innovation, on_delete=models.CASCADE, related_name="innovation"
    )
    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviewer"
    )
    review = models.JSONField()
    status = models.BooleanField(default=True)
    is_seen = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "innovation_manager_reviews"

    def __str__(self):
        return str(self.id)


class FinalInnovationManagerReview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    innovation = models.ForeignKey(
       Innovation, on_delete=models.CASCADE, related_name="fim_reviews"
    )
    reviewer =models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="fim_review_creator"
    )
    review = models.TextField()
    action = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    is_seen = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "final_innovation_manager_reviews"

    def __str__(self):
        return str(self.id)


class Notifications(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    innovation = models.ForeignKey(
       Innovation, on_delete=models.CASCADE, related_name="notification_innovation", null=True, blank=True
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notification_sender"
    )
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notification_receipient", null=True, blank=True
    )
    notification = models.TextField()
    subject = models.CharField(max_length=255,null=True, blank=True)
    status = models.BooleanField(default=True)
    is_seen = models.BooleanField(default=False)
    date_sent = models.DateTimeField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "notifications"

    def __str__(self):
        return str(self.id)