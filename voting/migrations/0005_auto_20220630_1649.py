# Generated by Django 3.2.5 on 2022-06-30 13:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('voting', '0004_postcommentchildren_postcomments_postimages_postlikes_posts_postseen'),
    ]

    operations = [
        migrations.AddField(
            model_name='postcommentchildren',
            name='commentor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='commentor_comment_child', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='postcomments',
            name='commentor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='commentor_comment', to=settings.AUTH_USER_MODEL),
        ),
    ]
