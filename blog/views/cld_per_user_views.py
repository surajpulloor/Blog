from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from blog.models import Comment

def comment_likes_per_user(req):
    if req.user.is_authenticated:

        comment_likes_by_user = Comment.objects.filter(liked_users__id=req.user.id)

        return render(req, 'blog/get_comment_likes_per_user.html', {'comment_likes': comment_likes_by_user})

    else:
        next = req.GET.get('next', '/')
        return HttpResponseRedirect(reverse('blog:login') + "?next=" + next)
    
def comment_dislikes_per_user(req):
    if req.user.is_authenticated:

        comment_dislikes_by_user = Comment.objects.filter(disliked_users__id=req.user.id)

        return render(req, 'blog/get_comment_dislikes_per_user.html', {'comment_dislikes': comment_dislikes_by_user})

    else:
        next = req.GET.get('next', '/')
        return HttpResponseRedirect(reverse('blog:login') + "?next=" + next)