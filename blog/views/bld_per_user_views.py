from django.http.response import  HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from blog.models import Blog

def blog_likes_per_user(req):
    
    if req.user.is_authenticated:

        blog_likes_by_user = Blog.objects.filter(liked_users__id=req.user.id)

        return render(req, 'blog/get_blog_likes_per_user.html', {'blog_likes': blog_likes_by_user})

    else:
        next = req.GET.get('next', '/')
        return HttpResponseRedirect(reverse('blog:login') + "?next=" + next)



def blog_dislikes_per_user(req):
    if req.user.is_authenticated:

        blog_dislikes_by_user = Blog.objects.filter(disliked_users__id=req.user.id)

        return render(req, 'blog/get_blog_dislikes_per_user.html', {'blog_dislikes': blog_dislikes_by_user})

    else:
        next = req.GET.get('next', '/')
        return HttpResponseRedirect(reverse('blog:login') + "?next=" + next)