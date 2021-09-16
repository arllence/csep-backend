# Generated by Django 3.2.5 on 2021-09-16 05:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('innovation', '0008_evaluation_note'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('deadline', models.DateField()),
                ('file', models.FileField(upload_to='documents')),
                ('description', models.TextField()),
                ('status', models.BooleanField(default=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignment_creator', to=settings.AUTH_USER_MODEL)),
                ('innovation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='innovation.innovation')),
            ],
            options={
                'db_table': 'assignments',
            },
        ),
    ]
