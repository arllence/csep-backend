from rest_framework import serializers
from . import models

class SystemUsersSerializer(serializers.Serializer):
    UserId = serializers.CharField()
    email = serializers.CharField()
    firstname = serializers.CharField()
    lastname = serializers.CharField()



class SkillsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Skills
        fields = '__all__'


class EmploymentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EmploymentStatus
        fields = '__all__'


