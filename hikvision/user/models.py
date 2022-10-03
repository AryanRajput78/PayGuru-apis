from distutils.command.upload import upload
from django.db import models
from django.db import models
from django.utils import timezone
from device.models import deviceDetails

import datetime
import pytz

# Create your models here.

def upload_to(instance, filename):
    return '/hikvision/images/{filename}'.format(filename=filename)

class userDetails(models.Model):
    class genderChoice(models.TextChoices):
        Male = 'Male'
        Female = 'Female'
        Non = 'None'

    class levelChoice(models.TextChoices):
        User = 'User'
        Visitor = 'Visitor'
        Blocklist = 'Blocklist'

    IP = models.ForeignKey(deviceDetails, on_delete=models.CASCADE)
    Name = models.CharField(max_length=25, blank=True)
    gender = models.CharField(blank=True, choices=genderChoice.choices, max_length=6)
    level = models.CharField(blank=True, choices=levelChoice.choices, max_length=10, default=levelChoice.User)
    floor_number = models.IntegerField(blank=True, null=True)
    room_number = models.IntegerField(blank=True, null=True)
    start_time = models.DateTimeField(default=timezone.now, editable=True)
    end_time = models.DateTimeField(default=datetime.datetime(2037, 12, 31, 23, 59, 59, tzinfo=pytz.UTC), editable=True)
    image = models.ImageField(upload_to=upload_to, null=True, blank=True)