import uuid
from django.db import models
from user_manager.models import User
from app_manager import models as app_manager_models




class Positions(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "positions"

    def __str__(self):
        return str(self.name)

class CandidatePosition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate = models.ForeignKey(
       User, on_delete=models.CASCADE, related_name="applicant"
    )
    position = models.ForeignKey(
       Positions, on_delete=models.CASCADE, related_name="position"
    )
    application_status = models.CharField(max_length=255, default="PENDING")
    status = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "candidate_position"

    def __str__(self):
        return str(self.candidate)
