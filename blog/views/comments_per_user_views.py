from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from blog.models import UserAnalytics

def comments_given_per_user(req):
    if req.user.is_authenticated:

        user = UserAnalytics.objects.get(user=req.user)
        comments_given_by_user = user.comments_given.all()

        return render(req, 'blog/get_comments_given_per_user.html', {'comments_given': comments_given_by_user})

    else:
        next = req.GET.get('next', '/')
        return HttpResponseRedirect(reverse('blog:login') + "?next=" + next)