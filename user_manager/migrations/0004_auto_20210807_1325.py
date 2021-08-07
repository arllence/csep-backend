# Generated by Django 3.2.5 on 2021-08-07 10:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('user_manager', '0003_rename_activity_otpcodes_otp'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='gender',
        ),
        migrations.RemoveField(
            model_name='user',
            name='phone_number',
        ),
        migrations.AlterField(
            model_name='user',
            name='is_defaultpassword',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('profile_picture', models.ImageField(blank=True, upload_to='profile_images')),
                ('phone_number', models.CharField(max_length=50)),
                ('gender', models.CharField(max_length=50)),
                ('about', models.TextField()),
                ('age', models.CharField(max_length=100)),
                ('disability', models.TextField()),
                ('country', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('physical_address', models.CharField(max_length=100)),
                ('county', models.CharField(max_length=100)),
                ('postal_code', models.CharField(max_length=100)),
                ('education_level', models.CharField(max_length=100)),
                ('employment_status', models.CharField(max_length=100)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_profile_info', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_info',
            },
        ),
        migrations.CreateModel(
            name='Skills',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'skills',
            },
        ),
    ]
