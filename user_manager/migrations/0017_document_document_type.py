# Generated by Django 3.2.5 on 2022-01-10 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_manager', '0016_alter_userinfo_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='document_type',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]