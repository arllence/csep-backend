# Generated by Django 3.2.5 on 2021-09-20 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('innovation', '0011_assignment_assignment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='assignment_status',
            field=models.CharField(default='PENDING', max_length=100),
        ),
    ]