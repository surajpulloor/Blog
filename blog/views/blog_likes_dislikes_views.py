from django.http.response import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse


from blog.models import Blog

def set_like(req, blogid):
    try:

        if req.user.is_authenticated:

            blog = get_object_or_404(Blog, pk=blogid)


            if blog.liked_users.filter(id=req.user.id).count() == 0:
                blog.liked_users.add(req.user)
                blog.noOfLikes += 1

                if blog.disliked_users.filter(id=req.user.id).count():
                    blog.disliked_users.remove(req.user)
                    blog.noOfDisLikes -= 1
            else:    
                blog.liked_users.remove(req.user)
                blog.noOfLikes -= 1


            blog.save()


            return HttpResponseRedirect(reverse('blog:get_blog', kwargs={'blog': blogid}) + "?next=0")
        else:
            next = req.GET.get('next', '/')
            return HttpResponseRedirect(reverse('blog:login') + "?next=" + next)
    except Blog.DoesNotExist:
        raise Http404("The blog doesn't exists.")



def set_dislike(req, blogid):
    try:

        if req.user.is_authenticated:

            blog = get_object_or_404(Blog, pk=blogid)

            if blog.disliked_users.filter(id=req.user.id).count() == 0:
                blog.disliked_users.add(req.user)
                blog.noOfDisLikes += 1

                if blog.liked_users.filter(id=req.user.id).count():
                    blog.liked_users.remove(req.user)
                    blog.noOfLikes -= 1
            else:    
                blog.disliked_users.remove(req.user)
                blog.noOfDisLikes -= 1
                        
            blog.save()


            return HttpResponseRedirect(reverse('blog:get_blog', kwargs={'blog': blogid}) + "?next=0")
        else:
            next = req.GET.get('next', '/')
            return HttpResponseRedirect(reverse('blog:login') + "?next=" + next)
    except Blog.DoesNotExist:
        raise Http404("The blog doesn't exists.")
