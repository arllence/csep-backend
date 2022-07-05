# Generated by Django 3.2.5 on 2022-07-05 13:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('voting', '0007_votes'),
    ]

    operations = [
        migrations.CreateModel(
            name='HasVoted',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('voter', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='has_voted', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'has_voted',
            },
        ),
    ]
