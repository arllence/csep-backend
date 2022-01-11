# Generated by Django 3.2.5 on 2022-01-10 08:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_manager', '0018_association_expiration'),
    ]

    operations = [
        migrations.AddField(
            model_name='association',
            name='document',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_Documents', to='user_manager.document'),
        ),
    ]