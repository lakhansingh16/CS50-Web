from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.core.paginator import Paginator

from .models import User, profile, Posts, Like

#function to load default view
def index(request):
    posts = Posts.objects.all().order_by('id').reverse()
    paginator = Paginator(posts, 10)
    page_no = request.GET.get('page')
    page_object = paginator.get_page(page_no)

    return render(request, "network/index.html", {'page_obj': page_object})


def login_view(request):
    if request.method == "POST": 
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

#function to create a new post
def Newpost(request, username):
    if request.method == 'POST':
        user = get_object_or_404(User, username=username)
        post_content = request.POST["textarea"]
        if not post_content:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        post = Posts()
        post.content=post_content
        post.user=user
        post.save()
        return redirect(index)

#function to view a user profile
@login_required(login_url="/login")
def profile_view(request,username):
    if request.method == 'GET':
        loggeduser = request.user
        profileuser = get_object_or_404(User, username=username)
        posts = Posts.objects.filter(user=profileuser).order_by('id').reverse()
        follower = profile.objects.filter(target=profileuser)
        following = profile.objects.filter(follower=profileuser)

        following_each_other = profile.objects.filter(follower=loggeduser, target=profileuser)
        totalfollower = follower.count()
        totalfollowing = following.count()
        paginator = Paginator(posts, 10)
        page_no = request.GET.get('page')
        page_object = paginator.get_page(page_no)

        context = {
            'posts': posts.count(),
            'totalfollowing': totalfollowing,
            'follower': follower,
            'totalfollower': totalfollower,
            'following': following,
            'page_obj': page_object,
            'profileuser': profileuser,
            'followingEachOther': following_each_other
        }

        return render(request, "network/profile.html", context)
    
    else:
        loggeduser = request.user
        profileuser = get_object_or_404(User, username=username)
        posts = Posts.objects.filter(user=profileuser).order_by('id').reverse()
        following_each_other = profile.objects.filter(follower=request.user, target=profileuser)
        paginator = Paginator(posts, 10)
        page_no = request.GET.get('page')
        page_object = paginator.get_page(page_no)
        if not following_each_other:
            follow = profile()
            follow.target = profileuser
            follow.follower = loggeduser
            follow.save()
            follower = profile.objects.filter(target=profileuser)
            following = profile.objects.filter(follower=profileuser)
            following_each_other = profile.objects.filter(follower=request.user, target=profileuser)
            totalfollower = follower.count()
            totalfollowing = following.count()

            context = {
                'profileuser': profileuser,
                'posts': posts.count(),
                'totalfollowing': totalfollowing,
                'followingEachOther': following_each_other,
                'follower': follower,
                'following': following,
                'page_obj': page_object,
                'totalfollower': totalfollower,
            }

            return render(request, "network/profile.html", context)

        else:
            following_each_other.delete()
            follower = profile.objects.filter(target=profileuser)
            following = profile.objects.filter(follower=profileuser)
            totalfollower = len(follower)
            totalfollowing = len(following)

            context = {
                'posts': posts.count(),
                'profileuser': profileuser,
                'page_obj': page_object,
                'follower': follower,
                'following': following,
                'totalfollowing': totalfollowing,
                'totalfollower': totalfollower,
                'followingEachOther': following_each_other
            }
            return render(request, "network/profile.html", context)


def all_posts(request):
    posts = Posts.objects.all().order_by('id').reverse()
    paginator = Paginator(posts, 10)
    page_no = request.GET.get('page')
    page_object = paginator.get_page(page_no)
    return render(request, "network/allposts.html", {'page_obj': page_object})
#function to like posts
def like_post(request,postid):
    user = request.user
    if request.method == 'GET':
        post_id = postid
        likedpost = Posts.objects.get(pk=post_id)
        #checks if user already liked the post
        if user in likedpost.liked.all():
            likedpost.liked.remove(user)
            like = Like.objects.get(post=likedpost, user=user)
            like.delete()
            return redirect(index)
        #if user did not like the post before
        else:
            like = Like.objects.get_or_create(post=likedpost, user=user)
            likedpost.liked.add(user)
            likedpost.save()
            return redirect(index)

#function that loads al the users that the logged in user is following
@login_required(login_url="/login")
def following_users(request, username):
    if request.method == 'GET':
        loggeduser = get_object_or_404(User, username=username)
        follows = profile.objects.filter(follower=loggeduser)
        posts = Posts.objects.all().order_by('id').reverse()
        postlist = []
        for post in posts:
            for follower in follows:
                if follower.target == post.user:
                    postlist.append(post)
        
        if not follows:
            return render(request, 'network/following.html', {'message': "You don't follow anybody."})

        paginator = Paginator(postlist, 10)
        page_no = request.GET.get("page")
        page_object = paginator.get_page(page_no)

        return render(request, 'network/following.html', {'page_obj':page_object})

def edit(request, post_id):
    if request.method == 'POST':
        post = Posts.objects.get(pk=post_id)
        textarea = request.POST["textarea"]
        post.content = textarea
        post.save()
        return redirect(index)
    else:
        post=Posts.objects.get(pk=post_id)
        return render(request,'network/edit.html',{'post_object':post})


