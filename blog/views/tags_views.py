from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse


from blog.forms import TagForm, DisabledTagForm
from blog.models import Blog, Tags


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
