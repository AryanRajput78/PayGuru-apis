# Generated by Django 4.1 on 2022-09-20 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="deviceDetails",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ip", models.GenericIPAddressField(null=True, unique=True)),
                ("port", models.IntegerField(default=80)),
                ("user_id", models.CharField(max_length=10)),
                ("password", models.CharField(max_length=10)),
                (
                    "master_status",
                    models.CharField(choices=[("YES", "Y"), ("NO", "N")], max_length=3),
                ),
            ],
        ),
    ]