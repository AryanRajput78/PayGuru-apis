# Generated by Django 4.1 on 2022-09-21 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0002_alter_userdetails_ip"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userdetails",
            name="gender",
            field=models.CharField(
                blank=True,
                choices=[("Male", "Male"), ("Female", "Female"), ("None", "Non")],
                max_length=6,
            ),
        ),
        migrations.AlterField(
            model_name="userdetails",
            name="level",
            field=models.CharField(
                blank=True,
                choices=[
                    ("User", "User"),
                    ("Visitor", "Visitor"),
                    ("Blocklist", "Blocklist"),
                ],
                default="User",
                max_length=10,
            ),
        ),
    ]
