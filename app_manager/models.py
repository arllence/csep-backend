import uuid
from django.db import models

class SupportServices(models.Model):
    id = models.AutoField(primary_key=True)
    service = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "app_manager"
        db_table = "support_services"

    def __str__(self):
        return str(self.service)


class Industry(models.Model):
    name = models.CharField(max_length=100)
    status = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "app_manager"
        db_table = "industry"

    def __str__(self):
        return str(self.name)


class DevelopmentStage(models.Model):
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "app_manager"
        db_table = "development_stage"

    def __str__(self):
        return str(self.name)


class IntellectualProperty(models.Model):
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "app_manager"
        db_table = "intellectual_property"

    def __str__(self):
        return str(self.name)