from django.contrib import admin
from user_manager import models as user_models

class SearchUser(admin.ModelAdmin):
    search_fields = ['email']
    class Meta:
        model = user_models.User


admin.site.register(user_models.User, SearchUser)