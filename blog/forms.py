
from django import forms
from django.contrib.auth.models import User

from blog.models import Blog, Comment, Tags

class LoginForm(forms.Form):
    
    username = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), max_length=20)

    


class SignUpForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'})
        }


class TagForm(forms.ModelForm):

    class Meta:
        model = Tags

        exclude = ('user',)
        fields = ['tag_name']
        widgets = {
            'tag_name': forms.TextInput(attrs={'class': "form-control", "autofocus": True}),
        }


class DisabledTagForm(forms.ModelForm):

    class Meta:
        model = Tags

        exclude = ('user',)
        fields = ['tag_name']
        widgets = {
            'tag_name': forms.TextInput(attrs={'class': "form-control", 'disabled': True}),
        }


class BlogForm(forms.ModelForm):

    class Meta:
        model = Blog

        exclude = ('user',)
        fields = ['title', 'body', 'isVisible', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': "form-control", 'autofocus': True}),
            'body': forms.Textarea(attrs={'cols': 40, 'rows': 20, 'class': "form-control"}),
            'tags': forms.CheckboxSelectMultiple()
        }

class DisabledBlogForm(forms.ModelForm):

    class Meta:
        model = Blog

        exclude = ('user',)
        fields = ['title', 'body', 'isVisible', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': "form-control", 'disabled': True, 'autofocus': True}),
            'body': forms.Textarea(attrs={'cols': 40, 'rows': 20, 'class': "form-control", 'disabled': True}),
            'isVisible': forms.CheckboxInput(attrs={'disabled': True}),
            'tags': forms.CheckboxSelectMultiple(attrs={'disabled': True})
        }


class CommentForm(forms.Form):
    
    body = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': True}))


class DisabledCommentForm(forms.Form):
    
    body = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}), disabled=True)