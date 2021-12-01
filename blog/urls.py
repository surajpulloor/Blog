from django.urls.conf import path

from blog.views import (login_form, 
                        dashboard, 
                        signout_form, 
                        get_users, 
                        get_blogs, 
                        get_blog, 
                        signup,
                        create_blog,
                        update_blog,
                        delete_blog,
                        set_like,
                        set_dislike,
                        add_comment,
                        update_comment,
                        delete_comment,
                        create_reply_comment,
                        update_reply_comment,
                        delete_reply_comment,
                        set_comment_like,
                        set_comment_dislike,
                        create_tag,
                        update_tag,
                        delete_tag,
                        pin_comment
                        )

app_name="blog"

urlpatterns = [
    path('login', login_form, name="login"),
    path('dashboard', dashboard, name="dashboard"),
    path('signout', signout_form, name="signout"),
    path('', get_users, name="get_users"),
    path('signup', signup, name="signup"),

    # blog access
    path('<int:blog>', get_blog, name="get_blog"),
    path('<int:user>/blogs', get_blogs, name="get_blogs"),

    # blog likes, dislikes
    path('<int:blogid>/like', set_like, name="set_like"),
    path('<int:blogid>/dislike', set_dislike, name="set_dislike"),

    # comment likes, dislikes
    path('<int:commentid>/like/comment', set_comment_like, name="set_comment_like"),
    path('<int:commentid>/dislike/comment', set_comment_dislike, name="set_comment_dislike"),

    # blog 
    path('create_blog', create_blog, name="create_blog"),
    path('update/<int:blogid>', update_blog, name="update_blog"),
    path('delete/<int:blogid>', delete_blog, name="delete_blog"),


    # tag 
    path('create_tag', create_tag, name="create_tag"),
    path('<int:tagid>/update/tag', update_tag, name="update_tag"),
    path('<int:tagid>/delete/tag', delete_tag, name="delete_tag"),


    # comments
    path('<int:blogid>/add/comment', add_comment, name="add_comment"),
    path('<int:blogid>/<int:commentid>/update/comment', update_comment, name="update_comment"),
    path('<int:blogid>/<int:commentid>/delete/comment', delete_comment, name="delete_comment"),

    # pin comment
    path('<int:commentid>/pin/comment', pin_comment, name="pin_comment"),

    # reply comments
    path('<int:blogid>/<int:commentid>/reply/comment', create_reply_comment, name="add_reply"),
    path('<int:blogid>/<int:commentid>/<int:reply_commentid>/update/reply/comment', update_reply_comment, name="update_reply"),
    path('<int:blogid>/<int:commentid>/<int:reply_commentid>/delete/reply/comment', delete_reply_comment, name="delete_reply"),


]
