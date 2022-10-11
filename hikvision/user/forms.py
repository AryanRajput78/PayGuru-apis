import django
from django import forms
from django.db import models
from django.forms import fields
from .models import userDetails
from django import forms

class image(forms.ModelForm):
    class Meta:
        model = userDetails
        fields = "__all__"