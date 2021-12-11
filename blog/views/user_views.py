from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse

from blog.forms import LoginForm, SignUpForm
from blog.models import Blog, Tags


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
