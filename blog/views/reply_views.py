from django.http.response import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.urls import reverse

from blog.exceptions import ReplyToCommentBySameUser
from blog.forms import CommentForm, DisabledCommentForm
from blog.models import Blog, Comment, UserAnalytics


def create_reply_comment(req, blogid, commentid):
    
    try:
        if req.user.is_authenticated:

            b = Blog.objects.get(blogid=blogid)
            head_comment = Comment.objects.get(comment_id=commentid)

            if head_comment.comment_user.id != req.user.id:

                if req.method == 'POST':

                    form = CommentForm(req.POST)

                    if form.is_valid():

                        if head_comment.isRoot:
                            # create reply comment
                            reply_comment = Comment.objects.create(
                                blog=b, 
                                comment_user=req.user, 
                                body=form.cleaned_data['body'], 
                                isRoot=False, 
                                head_comment=head_comment,
                                root_comment=head_comment,
                                pinned_timestamp=timezone.now()
                            )
                            
                        else:
                            # create reply comment
                            reply_comment = Comment.objects.create(
                                blog=b, 
                                comment_user=req.user, 
                                body=form.cleaned_data['body'], 
                                isRoot=False, 
                                head_comment=head_comment,
                                root_comment=head_comment.root_comment,
                                pinned_timestamp=timezone.now()
                            )


                        # Add the reply comment to the UserAnalytics table
                        if UserAnalytics.objects.filter(user=req.user).count() == 0:
                            user_analytics = UserAnalytics.objects.create(user=req.user)
                        else:
                            user_analytics = UserAnalytics.objects.get(user=req.user)

                        user_analytics.replies_given.add(reply_comment)
                        user_analytics.save()
                            

                        b.noOfComments += 1

                        b.save()
                        reply_comment.save()

                        return HttpResponseRedirect(reverse('blog:get_blog', kwargs={'blog': blogid}) + "?next=0")
            
                else:
                    form = CommentForm()

                return render(req, 'blog/create_reply_comment.html', {'form': form, 'blog': b, 'comment': head_comment})

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
        raise Http404("You cannot comment on your own comment")



def update_reply_comment(req, blogid, commentid, reply_commentid):
    
    try:
        if req.user.is_authenticated:

            b = Blog.objects.get(blogid=blogid)
            head_comment = Comment.objects.get(comment_id=commentid)
            reply_comment = Comment.objects.get(comment_id=reply_commentid, head_comment=head_comment)


            if reply_comment.comment_user.id == req.user.id:

                if req.method == 'POST':

                    form = CommentForm(req.POST)

                    if form.is_valid():
                        reply_comment.body = form.cleaned_data['body']
                        reply_comment.save()

                        next = req.GET.get('next', '/')
                        if next != '/':
                            return HttpResponseRedirect(next)
                        else:
                            return HttpResponseRedirect(reverse('blog:get_blog', kwargs={'blog': blogid}) + "?next=0")

                else:
                    form = CommentForm(initial={'body': reply_comment.body})

                return render(req, 'blog/update_reply_comment.html', {'form': form, 'blog': b, 'comment': head_comment})

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
        raise Http404("You cannot update this    liked_users = models.ManyToManyField(User, blank=True, related_name='blog_comment_liked_users') reply comment.")





def delete_reply_comment(req, blogid, commentid, reply_commentid):
    try:
        if req.user.is_authenticated:

            b = Blog.objects.get(blogid=blogid)
            head_comment = Comment.objects.get(comment_id=commentid)
            reply_comment = Comment.objects.get(comment_id=reply_commentid)


            if reply_comment.comment_user.id == req.user.id:

                if req.method == 'POST':

                    form = DisabledCommentForm(req.POST)

                    # Remove the comment to the UserAnalytics table
                    user_analytics = UserAnalytics.objects.get(user=req.user)
                    user_analytics.replies_given.remove(reply_comment)
                    user_analytics.save()


                    if Comment.objects.filter(head_comment=reply_comment).count() == 0:

                        head_comment2 = reply_comment.head_comment
                        reply_comment.delete()

                        # delete marked head_comment
                        leaf_comment = Comment.objects.get(comment_id=reply_comment.head_comment.comment_id)
                        while leaf_comment.isDeleted and Comment.objects.filter(head_comment=head_comment2).count() == 0:

                            head_comment2 = leaf_comment.head_comment
                            new_leaf_comment = Comment.objects.get(comment_id=leaf_comment.head_comment.comment_id)
                            leaf_comment.delete()
                            leaf_comment = new_leaf_comment


                    else:
                        reply_comment.isDeleted = not reply_comment.isDeleted
                        reply_comment.save()

                    
                    b.noOfComments = Comment.objects.filter(isDeleted=False).count()
                    b.save()
                        

                    next = req.GET.get('next', '/')
                    if next != '/':
                        return HttpResponseRedirect(next)
                    else:
                        return HttpResponseRedirect(reverse('blog:get_blog', kwargs={'blog': blogid}) + "?next=0")


                else:
                    form = DisabledCommentForm(initial={'body': reply_comment.body})

                return render(req, 'blog/delete_reply_comment.html', {'form': form, 'blog': b, 'comment': head_comment, 'reply_comment': reply_comment})

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
        raise Http404("You cannot delete this reply comment.")
