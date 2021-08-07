from .models import UserInfo
from django import forms

class PictureUploadForm(forms.Form):
    document = forms.FileField()
    class Meta:
        model = UserInfo
        fields = ['profile_picture']


    