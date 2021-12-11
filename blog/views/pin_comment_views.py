from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.urls import reverse

from blog.models import Comment

def pin_comment(req, commentid):
    
    comment = get_object_or_404(Comment, pk=commentid)

    comment.is_pinned = not comment.is_pinned

    if comment.is_pinned:
        comment.pinned_timestamp = timezone.now()

    comment.save()

    next = req.GET.get('next', '/')

    if next != '/':
        return HttpResponseRedirect(next)
    else:
        return HttpResponseRedirect(reverse('blog:get_blog', kwargs={'blog': comment.blog.blogid}) + "?next=0")
