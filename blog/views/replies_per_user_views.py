from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from blog.models import UserAnalytics

def replies_given_per_user(req):
    if req.user.is_authenticated:

        user = UserAnalytics.objects.get(user=req.user)
        replies_given_by_user = user.replies_given.all()

        return render(req, 'blog/get_replies_given_per_user.html', {'replies_given': replies_given_by_user})

    else:
        next = req.GET.get('next', '/')
        return HttpResponseRedirect(reverse('blog:login') + "?next=" + next)