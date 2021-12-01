from django.db import models
from django.contrib.auth.models import User

from django_quill.fields import QuillField


class Tags(models.Model):
    tagid = models.BigAutoField(primary_key=True)
    tag_name = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.tag_name



class Blog(models.Model):
    blogid = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100)
    body = QuillField()
    creation_timestamp = models.DateTimeField(auto_now_add=True)
    modified_timestamp = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    isVisible = models.BooleanField()
    numberOfViews = models.IntegerField(default=0)
    noOfLikes = models.IntegerField(default=0)
    noOfDisLikes = models.IntegerField(default=0)
    noOfComments = models.IntegerField(default=0)
    noOfTags = models.IntegerField(default=0)

    tags = models.ManyToManyField(Tags, blank=True)


    def __str__(self):
        return "Blog " + str(self.blogid)



class Comment(models.Model):
    comment_id = models.BigAutoField(primary_key=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    comment_user = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_timestamp = models.DateTimeField(auto_now_add=True)
    modified_timestamp = models.DateTimeField(auto_now=True)
    body = models.CharField(max_length=200)
    isDeleted = models.BooleanField(default=False)
    isRoot = models.BooleanField(default=True)

    noOfLikes = models.IntegerField(default=0)
    noOfDisLikes = models.IntegerField(default=0)

    head_comment = models.ForeignKey('Comment', related_name="reply_head_comment", on_delete=models.CASCADE, null=True)
    root_comment = models.ForeignKey('Comment', related_name="reply_root_comment", on_delete=models.CASCADE, null=True)

    is_pinned = models.BooleanField(default=False)
    pinned_timestamp = models.DateTimeField()


    def __str__(self):
        return "Comment " + str(self.comment_id)
    


class Blog_Likes_DisLikes_PerUser(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    liked = models.BooleanField(default=False)
    disliked = models.BooleanField(default=False)


class Comment_Likes_DisLikes_PerUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    liked = models.BooleanField(default=False)
    disliked = models.BooleanField(default=False)