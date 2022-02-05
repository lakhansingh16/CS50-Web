from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:username>", views.profile_view, name="profile"),
    path("profile/<str:username>/newpost",views.Newpost,name="newpost"),
    path("likepost/<int:postid>", views.like_post, name='likepost'),
    path("following/<str:username>", views.following_users, name='following'),
    path("posts/<int:post_id>/edit", views.edit, name="edit"),
    path("allposts",views.all_posts,name="allposts")
]
