# Generated by Django 3.2.5 on 2021-09-28 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('innovation', '0017_auto_20210925_1015'),
    ]

    operations = [
        migrations.AddField(
            model_name='innovationmanagerreview',
            name='is_seen',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='innovationreview',
            name='is_seen',
            field=models.BooleanField(default=False),
        ),
    ]
