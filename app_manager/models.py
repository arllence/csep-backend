import uuid
from django.db import models

class Skills(models.Model):
    name = models.CharField(max_length=100)
    status = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "app_manager"
        db_table = "innovation_skills"

    def __str__(self):
        return str(self.name)


class EmploymentStatus(models.Model):
    name = models.CharField(max_length=100)
    status = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "app_manager"
        db_table = "employment_status"

    def __str__(self):
        return str(self.name)


class EducationLevel(models.Model):
    name = models.CharField(max_length=100)
    status = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "app_manager"
        db_table = "education_level"

    def __str__(self):
        return str(self.name)