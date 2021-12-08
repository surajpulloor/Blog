from django.urls.conf import path

from blog.views import (
                    dashboard,    
                    blog_likes_per_user,
                    blog_dislikes_per_user,
                    comment_likes_per_user,
                    comment_dislikes_per_user,
                    comments_given_per_user,
                    replies_given_per_user)

urlpatterns = [

    path('', dashboard, name="dashboard_home"),
    path('get_blog_likes', blog_likes_per_user, name="dashboard_get_blog_likes"),
    path('get_blog_dislikes', blog_dislikes_per_user, name="dashboard_get_blog_dislikes"),
    path('get_comment_likes', comment_likes_per_user, name="dashboard_get_comment_likes"),
    path('get_comment_dislikes', comment_dislikes_per_user, name="dashboard_get_comment_dislikes"),
    path('comments_given', comments_given_per_user, name="dashboard_comments_given_per_user"),
    path('replies_given', replies_given_per_user, name="dashboard_replies_given_per_user")

]
