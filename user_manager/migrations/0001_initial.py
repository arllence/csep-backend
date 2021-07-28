# Generated by Django 3.2.5 on 2021-07-28 12:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.CharField(max_length=100, unique=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('phone_number', models.CharField(max_length=50)),
                ('gender', models.CharField(max_length=50)),
                ('register_as', models.CharField(max_length=50)),
                ('hear_about_us', models.CharField(blank=True, max_length=255, null=True)),
                ('accepted_terms', models.BooleanField(default=False)),
                ('newsletter', models.BooleanField(default=False)),
                ('verified_email', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_defaultpassword', models.BooleanField(default=True)),
                ('is_suspended', models.BooleanField(null=True)),
                ('last_password_reset', models.DateTimeField(auto_now=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'systemusers',
            },
        ),
        migrations.CreateModel(
            name='AccountActivity',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('activity', models.TextField(blank=True, null=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('action_time', models.DateTimeField(auto_now_add=True)),
                ('actor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activity_actor', to=settings.AUTH_USER_MODEL)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_account_activity', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'account_activity',
            },
        ),
    ]
