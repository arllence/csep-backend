from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.SupportServices)
admin.site.register(models.Industry)
admin.site.register(models.IntellectualProperty)
admin.site.register(models.DevelopmentStage)
admin.site.register(models.Hubs)
admin.site.register(models.Skills)
admin.site.register(models.EmploymentStatus)
admin.site.register(models.EducationLevel)