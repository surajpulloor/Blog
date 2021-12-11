from django.http.response import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.urls import reverse

from blog.exceptions import ReplyToCommentBySameUser

from blog.forms import CommentForm, DisabledCommentForm
from blog.models import Blog, Comment, UserAnalytics


def add_comment(req, blogid):
    
    try:
        if req.user.is_authenticated:

            b = Blog.objects.get(blogid=blogid)

            if req.method == 'POST':

                form = CommentForm(req.POST)

                if form.is_valid():

                    
                    c = Comment.objects.create(
                            blog=b, 
                            comment_user=req.user, 
                            body=form.cleaned_data['body'],
                            root_comment=None,
                            pinned_timestamp = timezone.now()
                        )


                    # Add the reply comment to the UserAnalytics table
                    if UserAnalytics.objects.filter(user=req.user).count() == 0:
                        user_analytics = UserAnalytics.objects.create(user=req.user)
                    else:
                        user_analytics = UserAnalytics.objects.get(user=req.user)

                    user_analytics.comments_given.add(c)
                    user_analytics.save()

                    b.noOfComments += 1

                    b.save()
                    c.save()

                    return HttpResponseRedirect(reverse('blog:get_blog', kwargs={'blog': blogid}) + "?next=0")
            else:
                form = CommentForm()

            return render(req, 'blog/create_comment.html', {'form': form, 'blog': b})

        else:
            next = req.GET.get('next', '/')
            if next != '/':
                return HttpResponseRedirect(reverse('blog:login') + "?next=" + next)
            else:
                return HttpResponseRedirect(reverse('blog:login'))

    except Blog.DoesNotExist:
        raise Http404('The Blog does not exists')


def update_comment(req, blogid, commentid):
    try:
        if req.user.is_authenticated:

            b = Blog.objects.get(blogid=blogid)
            c = Comment.objects.get(comment_id=commentid)

            if c.comment_user.id == req.user.id:

                if req.method == 'POST':

                    form = CommentForm(req.POST)

                    if form.is_valid():
                        c.body = form.cleaned_data['body']
                        c.save()


                        next = req.GET.get('next', '/')
                        if next != '/':
                            return HttpResponseRedirect(next)
                        else:
                            return HttpResponseRedirect(reverse('blog:get_blog', kwargs={'blog': blogid}) + "?next=0")
                else:
                    form = CommentForm(initial={'body': c.body})

                return render(req, 'blog/update_comment.html', {'form': form, 'blog': b})

            else:
                raise ReplyToCommentBySameUser("")


        else:
            next = req.GET.get('next', '/')
            if next != '/':
                return HttpResponseRedirect(reverse('blog:login') + "?next=" + next)
            else:
                return HttpResponseRedirect(reverse('blog:login'))


    except Blog.DoesNotExist:
        raise Http404('The Blog does not exists')
    except Comment.DoesNotExist:
        raise Http404('The Comment does not exists')

    except ReplyToCommentBySameUser:
        raise Http404("You don't own this comment, so cannot update.") 


def delete_comment(req, blogid, commentid):
    try:
        if req.user.is_authenticated:

            b = Blog.objects.get(blogid=blogid)
            c = Comment.objects.get(comment_id=commentid)

            if c.comment_user.id == req.user.id:

                if req.method == 'POST':

                    form = DisabledCommentForm(req.POST)
                    
                    b.noOfComments -= Comment.objects.filter(root_comment=c).count() + 1

                    # Remove the comment to the UserAnalytics table
                    user_analytics = UserAnalytics.objects.get(user=req.user)
                    user_analytics.comments_given.remove(c)
                    user_analytics.save()

                    b.save()
                    c.delete()

                    next = req.GET.get('next', '/')
                    if next != '/':
                        return HttpResponseRedirect(next)
                    else:
                        return HttpResponseRedirect(reverse('blog:get_blog', kwargs={'blog': blogid}) + "?next=0")

                else:
                    form = DisabledCommentForm(initial={'body': c.body})

                return render(req, 'blog/delete_comment.html', {'form': form, 'blog': b})

            else:
                raise ReplyToCommentBySameUser("")

        else:
            next = req.GET.get('next', '/')
            if next != '/':
                return HttpResponseRedirect(reverse('blog:login') + "?next=" + next)
            else:
                return HttpResponseRedirect(reverse('blog:login'))


    except Blog.DoesNotExist:
        raise Http404('The Blog does not exists')
    except Comment.DoesNotExist:
        raise Http404('The Comment does not exists')

    except ReplyToCommentBySameUser:
        raise Http404("You don't own this comment, so cannot delete.")
