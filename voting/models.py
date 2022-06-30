import uuid
from django.db import models
from user_manager.models import User
from app_manager import models as app_manager_models




class Positions(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "positions"

    def __str__(self):
        return str(self.name)

class CandidatePosition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate = models.ForeignKey(
       User, on_delete=models.CASCADE, related_name="applicant"
    )
    position = models.ForeignKey(
       Positions, on_delete=models.CASCADE, related_name="position"
    )
    application_status = models.CharField(max_length=255, default="PENDING")
    status = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "candidate_position"

    def __str__(self):
        return str(self.candidate)


class Posts(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate = models.ForeignKey(
       User, on_delete=models.CASCADE, related_name="candidate_post"
    )
    post = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "posts"

    def __str__(self):
        return str(self.candidate)


class PostImages(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(
       Posts, on_delete=models.CASCADE, related_name="post_image"
    )
    image = models.ImageField()
    status = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "post_images"

    def __str__(self):
        return str(self.post)


class PostComments(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    commentor = models.ForeignKey(
       User, on_delete=models.CASCADE, related_name="commentor_comment", null=True
    )
    post = models.ForeignKey(
       Posts, on_delete=models.CASCADE, related_name="post_comment"
    )
    comment = models.TextField()
    status = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "post_comments"

    def __str__(self):
        return str(self.post)


class PostCommentChildren(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    commentor = models.ForeignKey(
       User, on_delete=models.CASCADE, related_name="commentor_comment_child", null=True
    )
    comment = models.ForeignKey(
       PostComments, on_delete=models.CASCADE, related_name="post_comment"
    )
    child = models.TextField()
    status = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "post_comment_children"

    def __str__(self):
        return str(self.comment)


class PostLikes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(
       Posts, on_delete=models.CASCADE, related_name="post_like"
    )
    liker = models.ForeignKey(
       User, on_delete=models.CASCADE, related_name="post_liker"
    )
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "post_likes"

    def __str__(self):
        return str(self.post)


class PostSeen(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(
       Posts, on_delete=models.CASCADE, related_name="post_seen"
    )
    user = models.ForeignKey(
       User, on_delete=models.CASCADE, related_name="seen_post"
    )
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "post_seen"

    def __str__(self):
        return str(self.post)

