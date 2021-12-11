from django.http.response import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse

from blog.models import Blog, Comment


# comment likes, dislikes
def set_comment_like(req, commentid):
    try:

        if req.user.is_authenticated:

            comment = get_object_or_404(Comment, pk=commentid)

            if comment.liked_users.filter(id=req.user.id).count():
                comment.noOfLikes -= 1
                comment.liked_users.remove(req.user)
            else:
                comment.noOfLikes += 1
                comment.liked_users.add(req.user)

                if comment.disliked_users.filter(id=req.user.id).count():
                    comment.noOfDisLikes -= 1
                    comment.disliked_users.remove(req.user)            
                        
            comment.save()


            next = req.GET.get('next', '/')

            if next != '/':
                return HttpResponseRedirect(next)
            else:
                return HttpResponseRedirect(reverse('blog:get_blog', kwargs={'blog': comment.blog.blogid}) + "?next=0")
        else:
            next = req.GET.get('next', '/')
            return HttpResponseRedirect(reverse('blog:login') + "?next=" + next)
    except Blog.DoesNotExist:
        raise Http404("The blog doesn't exists.")
        



def set_comment_dislike(req, commentid):
    try:

        if req.user.is_authenticated:

            comment = get_object_or_404(Comment, pk=commentid)


            if comment.disliked_users.filter(id=req.user.id).count():
                comment.noOfDisLikes -= 1
                comment.disliked_users.remove(req.user)
            else:
                comment.noOfDisLikes += 1
                comment.disliked_users.add(req.user)

                if comment.liked_users.filter(id=req.user.id).count():
                    comment.noOfLikes -= 1
                    comment.liked_users.remove(req.user)            
                        
            
            comment.save()


            next = req.GET.get('next', '/')

            if next != '/':
                return HttpResponseRedirect(next)
            else:
                return HttpResponseRedirect(reverse('blog:get_blog', kwargs={'blog': comment.blog.blogid}) + "?next=0")
        else:
            next = req.GET.get('next', '/')
            return HttpResponseRedirect(reverse('blog:login') + "?next=" + next)
    except Blog.DoesNotExist:
        raise Http404("The blog doesn't exists.")
