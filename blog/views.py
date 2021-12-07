from datetime import time
from django import forms
from django.http.response import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.utils.timezone import now
from django.urls import reverse

from blog.exceptions import ReplyToCommentBySameUser

from .forms import LoginForm, SignUpForm, BlogForm, CommentForm, DisabledCommentForm, DisabledBlogForm, TagForm, DisabledTagForm

from .models import Blog, Comment, Comment_Likes_DisLikes_PerUser, Tags


def login_form(req):

    hasUsers = True

    if req.user.is_authenticated:
        return HttpResponseRedirect(reverse('blog:dashboard_home'))

    elif User.objects.count() == 0:
        hasUsers = False
        return render(req, "blog/login.html", {"hasUsers": hasUsers})
    else:
        error = {
            "username": "",
            "password": ""
        }

        if req.method == "POST":

            form = LoginForm(req.POST)

            if form.is_valid():
                user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
                    
                if user is not None:   
                    login(req, user)
                    next = req.GET.get('next', '/')

                    print(next)
                    if next != '/':
                        return HttpResponseRedirect(next)
                    else:
                        return HttpResponseRedirect(reverse('blog:dashboard_home'))
                else:
                    try:
                        user = User.objects.get(username=form.cleaned_data['username'])
                    except:
                        
                        error["username"] = "User name is not valid"

                    else:
                        error['password'] = "Password is incorrect"

        else:
            form = LoginForm()

        return render(req, "blog/login.html", {"form": form, 'error': error, "hasUsers": hasUsers})



def dashboard(req):
    if req.user.is_authenticated:
        blogs = Blog.objects.filter(user=req.user)
        tags = Tags.objects.filter(user=req.user)
        return render(req, "blog/dashboard.html", {"user": req.user, 'blogs': blogs, 'tags': tags})
    else:
        return HttpResponseRedirect(reverse('blog:login'))


def signout_form(req):
    if req.user.is_authenticated:
        logout(req)

    next = req.GET.get('next', '/')
    return HttpResponseRedirect(next)


def signup(req):
    
    if req.method == "POST":

        form = SignUpForm(req.POST)

        if form.is_valid():
            user = form.save()
            user.set_password(user.password)
            user.save()

            if req.user.is_authenticated:
                logout(req)
            
            next = req.GET.get('next', '/')

            next = ("?next=" + next) if next != '/' else ""

            return HttpResponseRedirect(reverse('blog:login') + next)
    else:
        form = SignUpForm()

    return render(req, 'blog/signup.html', { 'form': form })




def get_users(req):
    users = User.objects.filter(is_superuser=False)
    return render(req, 'blog/home.html', {'users': users})


def create_blog(req):
    if req.user.is_authenticated:

        if req.method == "POST":

            form = BlogForm(req.POST)

            if form.is_valid():


                print(form.cleaned_data['tags'])

                blog = form.save(commit=False)
                blog.user = req.user
                blog.modified_timestamp=now()
                blog.save()

                tags = form.cleaned_data['tags']
                noOfTags = 0

                for tag in tags:
                    blog.tags.add(Tags.objects.get(tag_name=tag))
                    noOfTags += 1

                

                blog.noOfTags = noOfTags
                blog.save()

                return HttpResponseRedirect(reverse('blog:dashboard_home'))

        else:
            form = BlogForm()

        return render(req, 'blog/create_blog.html', {'form': form})

    else:
        return HttpResponseRedirect(reverse('blog:login'))


def get_blogs(req, user):
    
    userO = get_object_or_404(User, pk=user)
    blogs = Blog.objects.filter(user=userO, isVisible=True)
    

    return render(req, 'blog/blog_list.html', {'blogs': blogs})


def get_comment_section(comments, auth_user, root_comment_id=-1):
    comment_section = []

    # go through all the comments
    for comment in comments:
        
        # find out whether the comment is liked or not by the auth user
        if auth_user and Comment_Likes_DisLikes_PerUser.objects.filter(comment=comment, user=auth_user).count() > 0:
            comment_LD_perUser = Comment_Likes_DisLikes_PerUser.objects.get(comment=comment, user=auth_user)
            liked = comment_LD_perUser.liked
            disliked = comment_LD_perUser.disliked
        else:
            liked = False
            disliked = False

        comment_replies = {
            'comment': comment,
            'replies': [],
            'root_comment_id': (root_comment_id if root_comment_id != -1 else comment.comment_id),
            'liked': liked,
            'disliked': disliked
        }

        pinned_comments = Comment.objects.filter(head_comment=comment, is_pinned=True).order_by('-pinned_timestamp')
        unpinned_comment = Comment.objects.filter(head_comment=comment, is_pinned=False).order_by('-modified_timestamp')

        sub_comments = list(pinned_comments) + list(unpinned_comment)

        comment_replies['replies'] = get_comment_section(sub_comments, auth_user, comment.comment_id)

        comment_section.append(comment_replies)

    return comment_section

        

def get_blog(req, blog):

    try:
        blog = Blog.objects.get(pk=blog)

        if req.GET.get('next', '/') == '/':
            blog.numberOfViews += 1


        liked = False
        disLiked = False
        user = None

        if req.user.is_authenticated:

            # get Likes per User obj
            if blog.liked_users.filter(id=req.user.id).count():
                liked = True
            elif blog.disliked_users.filter(id=req.user.id).count():
                disLiked = True

            user = req.user

        
        pinned_comments = Comment.objects.filter(blog=blog, isRoot=True, is_pinned=True).order_by('-pinned_timestamp')
        unpinned_comment = Comment.objects.filter(blog=blog, isRoot=True, is_pinned=False).order_by('-modified_timestamp')

        comments = list(pinned_comments) + list(unpinned_comment)

        comment_section = get_comment_section(comments=comments, auth_user=user)


        blog.save()

        
        return render(req, 'blog/get_blog.html', {'blog': blog, 'liked': liked, 'disLiked': disLiked, 'comments': comment_section})
    except Blog.DoesNotExist:
        raise Http404("The blog doesn't exists.")


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




def update_blog(req, blogid):
    if req.user.is_authenticated:

        blog = get_object_or_404(Blog, pk=blogid)

        if req.method == 'POST':

            form = BlogForm(req.POST)

            if form.is_valid():
                
                blog.title = form.cleaned_data['title']
                blog.body = form.cleaned_data['body']
                blog.isVisible = form.cleaned_data['isVisible']
                blog.modified_timestamp = now()

                # update the tags
                # empty the tags 
                blog.tags.clear()

                blog.save()


                tags = form.cleaned_data['tags']
                noOfTags = 0

                for tag in tags:
                    blog.tags.add(Tags.objects.get(tag_name=tag))
                    noOfTags += 1

                
                blog.noOfTags = noOfTags
                blog.save()


                return HttpResponseRedirect(reverse('blog:dashboard_home'))

        else:
            form = BlogForm(instance=blog)

        return render(req, 'blog/update_blog.html', {'form': form, 'blogid': blogid})

    return HttpResponseRedirect(reverse('blog:login'))
                        
                        
def delete_blog(req, blogid):
    if req.user.is_authenticated:

        blog = get_object_or_404(Blog, pk=blogid)

        if req.method == 'POST':
            form = DisabledBlogForm(req.POST)
            Blog.objects.filter(pk=blogid).delete()
            return HttpResponseRedirect(reverse('blog:dashboard_home'))

        else:
            form = DisabledBlogForm(instance=blog)

        return render(req, 'blog/delete_blog.html', {'form': form, 'blogid': blogid})


    return HttpResponseRedirect(reverse('blog:login'))



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

                    b.save()
                    c.delete()

                    return HttpResponseRedirect(reverse('blog:get_blog', blogid) + "?next=0")

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
        raise Http404("You cannot update this reply comment.")





def delete_reply_comment(req, blogid, commentid, reply_commentid):
    try:
        if req.user.is_authenticated:

            b = Blog.objects.get(blogid=blogid)
            head_comment = Comment.objects.get(comment_id=commentid)
            reply_comment = Comment.objects.get(comment_id=reply_commentid)


            if reply_comment.comment_user.id == req.user.id:

                if req.method == 'POST':

                    form = DisabledCommentForm(req.POST)


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


# comment likes, dislikes
def set_comment_like(req, commentid):
    try:

        if req.user.is_authenticated:

            comment = get_object_or_404(Comment, pk=commentid)


            if Comment_Likes_DisLikes_PerUser.objects.filter(comment=comment, user=req.user).count() == 0:

                comment_LD_per_user = Comment_Likes_DisLikes_PerUser.objects.create(comment = comment, user = req.user, liked = True)
                comment.noOfLikes += 1
            else:
                comment_LD_per_user = Comment_Likes_DisLikes_PerUser.objects.get(comment=comment, user=req.user)

                if not comment_LD_per_user.liked:
                    comment.noOfLikes += 1

                    if comment_LD_per_user.disliked:
                        comment.noOfDisLikes -= 1

                else:    
                    comment.noOfLikes -= 1

                comment_LD_per_user.liked = not comment_LD_per_user.liked
                comment_LD_per_user.disliked = False



            comment_LD_per_user.save()
            comment.save()


            return HttpResponseRedirect('/home/' + str(comment.blog.blogid) + "?next=0")
        else:
            next = req.GET.get('next', '/')
            return HttpResponseRedirect(reverse('blog:login') + "?next=" + next)
    except Blog.DoesNotExist:
        raise Http404("The blog doesn't exists.")
        



def set_comment_dislike(req, commentid):
    try:

        if req.user.is_authenticated:

            comment = get_object_or_404(Comment, pk=commentid)


            if Comment_Likes_DisLikes_PerUser.objects.filter(comment=comment, user=req.user).count() == 0:

                comment_LD_per_user = Comment_Likes_DisLikes_PerUser.objects.create(comment = comment, user = req.user, disliked = True)
                comment.noOfDisLikes += 1
            else:
                comment_LD_per_user = Comment_Likes_DisLikes_PerUser.objects.get(comment=comment, user=req.user)

                if not comment_LD_per_user.disliked:
                    comment.noOfDisLikes += 1

                    if comment_LD_per_user.liked:
                        comment.noOfLikes -= 1
                        
                else:    
                    comment.noOfDisLikes -= 1

                comment_LD_per_user.disliked = not comment_LD_per_user.disliked
                comment_LD_per_user.liked = False



            comment_LD_per_user.save()
            comment.save()


            return HttpResponseRedirect('/home/' + str(comment.blog.blogid) + "?next=0")
        else:
            next = req.GET.get('next', '/')
            return HttpResponseRedirect(reverse('blog:login') + "?next=" + next)
    except Blog.DoesNotExist:
        raise Http404("The blog doesn't exists.")



def create_tag(req):
    
    if req.user.is_authenticated:
        
        if req.method == 'POST':

            form = TagForm(req.POST)

            if form.is_valid():
                tag = form.save(commit=False)
                tag.user = req.user
                tag.save()

                return HttpResponseRedirect(reverse('blog:dashboard_home'))

        else:

            form = TagForm()

        return render(req, 'blog/create_tags.html', {'form': form})

    else:
        next = req.GET.get('next', '/')
        return HttpResponseRedirect(reverse('blog:login') + "?next=" + next)



def update_tag(req, tagid):

    tag = get_object_or_404(Tags, pk=tagid)
    
    if req.user.is_authenticated:

        if req.method == "POST":

            form = TagForm(req.POST)

            if form.is_valid():
                tag.tag_name = form.cleaned_data['tag_name']
                tag.save()

                return HttpResponseRedirect(reverse('blog:dashboard_home'))

        else:

            form = TagForm(instance=tag)

        return render(req, 'blog/update_tags.html', {'form': form, 'tag': tag})

    else:
        next = req.GET.get('next', '/')
        return HttpResponseRedirect(reverse('blog:login') + "?next=" + next)



def delete_tag(req, tagid):

    tag = get_object_or_404(Tags, pk=tagid)
    
    if req.user.is_authenticated:

        if req.method == "POST":

            blogs = Blog.objects.filter(tags__tagid=tagid)

            # Decrement noOfTags for each blog this tag belongs to
            for blog in blogs:
                blog.noOfTags -= 1
                blog.save()

            tag.delete()

            return HttpResponseRedirect(reverse('blog:dashboard_home'))

        else:

            form = DisabledTagForm(instance=tag)

        return render(req, 'blog/delete_tags.html', {'form': form, 'tag': tag})

    else:
        next = req.GET.get('next', '/')
        return HttpResponseRedirect(reverse('blog:login') + "?next=" + next)



def pin_comment(req, commentid):
    
    comment = get_object_or_404(Comment, pk=commentid)

    comment.is_pinned = not comment.is_pinned

    if comment.is_pinned:
        comment.pinned_timestamp = timezone.now()

    comment.save()

    next = req.GET.get('next', '/')

    return HttpResponseRedirect(next)


def blog_likes_per_user(req):
    
    if req.user.is_authenticated:

        blog_likes_by_user = Blog.objects.filter(liked_users__id=req.user.id)

        return render(req, 'blog/get_likes_per_user.html', {'blog_likes': blog_likes_by_user})

    else:
        next = req.GET.get('next', '/')
        return HttpResponseRedirect(reverse('blog:login') + "?next=" + next)



def blog_dislikes_per_user(req):
    if req.user.is_authenticated:

        blog_dislikes_by_user = Blog.objects.filter(disliked_users__id=req.user.id)

        return render(req, 'blog/get_dislikes_per_user.html', {'blog_dislikes': blog_dislikes_by_user})

    else:
        next = req.GET.get('next', '/')
        return HttpResponseRedirect(reverse('blog:login') + "?next=" + next)
    
def comment_likes_per_user(req):
    pass
    
def comment_dislikes_per_user(req):
    pass
    
def comments_given_per_user(req):
    pass
    
def replies_given_per_user(req):
    pass