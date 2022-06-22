from django.contrib import admin
from voting import models as voting_models

# class SearchUser(admin.ModelAdmin):
#     search_fields = ['email']
#     class Meta:
#         model = user_models.User


# admin.site.register(user_models.User, SearchUser)
admin.site.register(voting_models.Positions)

