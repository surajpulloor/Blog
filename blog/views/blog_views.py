from django.http.response import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.urls import reverse


from blog.forms import BlogForm, DisabledBlogForm

from blog.models import Blog, Comment, Tags

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

        liked = False
        disliked = False

        # find out whether the comment is liked or not by the auth user
        if auth_user and comment.liked_users.filter(id=auth_user.id).count() > 0:
            liked = True
        elif auth_user and comment.disliked_users.filter(id=auth_user.id).count() > 0:
            disliked = True

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
