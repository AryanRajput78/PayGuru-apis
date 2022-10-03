# Generated by Django 4.1 on 2022-09-29 11:40

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0003_alter_userdetails_gender_alter_userdetails_level"),
    ]

    operations = [
        migrations.AddField(
            model_name="userdetails",
            name="image",
            field=models.FileField(default=1, upload_to="Face/%Y/%m/%d/"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="userdetails",
            name="end_time",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2037, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]