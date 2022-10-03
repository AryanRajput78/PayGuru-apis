from django.db import models

# Create your models here.

class deviceDetails(models.Model):
    class masterChoice(models.TextChoices):
        yes = "YES"
        no = "NO"
    class statChoice(models.TextChoices):
        Online = "Online"
        Offline = 'Offline'

    ip = models.GenericIPAddressField(null=True, blank=False, unique=True)
    port = models.IntegerField(blank=False, default=80)
    user_id = models.CharField(blank=False, max_length=10)
    password = models.CharField(blank=False, max_length=10)
    master_status = models.CharField(blank=False, choices=masterChoice.choices, default=masterChoice.no, max_length=3)
    status = models.CharField(blank=False, default=statChoice.Offline, choices=statChoice.choices, max_length=7)

    def __str__(self):
        return self.ip