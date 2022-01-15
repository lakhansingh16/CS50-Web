from typing import ItemsView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import User,activelistings, productcomments, Watchlist, Winner, bids


def index(request):
    return render(request, "auctions/index.html")
       

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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


#viewing active listings
@login_required(login_url="/login")
def active_listings(request):
    return render(request,"auctions/activelisting.html",{"articles": activelistings.objects.all()})


#creating a new listing
@login_required(login_url="/login")
def create_listing(request):
    if request.method == "GET":
        return render(request, "auctions/create.html")
    new = activelistings()
    new.article = request.POST.get("item_name")
    new.seller = request.user.username
    new.category = request.POST.get("category")
    new.description = request.POST.get("description")
    new.price = request.POST.get("price")
    if request.POST.get('link'):
        new.photo_link =request.POST.get("link")
    else:
        new.photo_link = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRkVoU30el-uCaUCGqyI_r4p9yELRynCgBe6W9eJtBn2HQ-If0V9IhtbmuNyOmOTc9JqM8&usqp=CAU"
    new.save()
    return HttpResponseRedirect(reverse("active_listings"))

#fucntion to view individual listing
@login_required(login_url="/login")
def listing(request,product_id):
    comment = productcomments.objects.filter(listingid=product_id)
    added = Watchlist.objects.filter(listingid=product_id, user=request.user.username)
    if request.method == "POST":
        item = activelistings.objects.get(id=product_id)
        newbid = int(request.POST.get('newbid'))
        # checking if the newbid is greater than or equal to current bid
        if item.price >= newbid:
            product = activelistings.objects.get(id=product_id)
            return render(request, "auctions/listing.html", {
                "product": product,
                "message": "Your Bid should be higher than the Current one.",
                "msg_type": "danger",
                "comments": comment,
            })
        else:
            item.price = newbid
            item.save()
            # saving the bid in Bid model
            bidobj = bids.objects.filter(listingid=product_id)
            if bidobj:
                bidobj.delete()
            new = bids()
            new.bidder = request.user.username
            new.title = item.article
            new.listingid = product_id
            new.bid_price = newbid
            new.save()
            product = activelistings.objects.get(id=product_id)
            return render(request, "auctions/listing.html", {
                "product": product,
                "message": "Your Bid is added.",
                "msg_type": "success",
                "comments": comment
            })
    else:
        article = activelistings.objects.get(id=product_id)
        return render(request, "auctions/listing.html", {"product": article,
        "comments": comment,
        "usernow":request.user.username,
        "added":added})


#To add a comment
@login_required(login_url="/login")
def addcomment(request,product_id):
    newcomment = productcomments()
    newcomment.comment = request.POST.get('comment')
    newcomment.person= request.user.username
    newcomment.listingid = product_id
    newcomment.save()
    comment = productcomments.objects.filter(listingid=product_id)
    product = activelistings.objects.get(id=product_id)
    added = Watchlist.objects.filter(
        listingid=product_id, user=request.user.username)
    return render(request, "auctions/listing.html", {
        "product": product,
        "added": added,
        "comments": comment
    })

#function to add items to watchlist
@login_required(login_url="/login")
def addtowatchlist(request,product_id):
    item = Watchlist.objects.filter(listingid=product_id, user=request.user.username)
    comments = productcomments.objects.filter(listingid=product_id)
    if item:
        item.delete()
        product = activelistings.objects.get(id=product_id)
        added = Watchlist.objects.filter(
            listingid=product_id, user=request.user.username)
        return render(request, "auctions/listing.html", {
            "product": product,
            "added": added,
            "comments": comments
        })
    else:
        # if it not present then the user wants to add it to watchlist
        new = Watchlist()
        new.user = request.user.username
        new.listingid = product_id
        new.save()
        # returning the updated content
        product = activelistings.objects.get(id=product_id)
        added = Watchlist.objects.filter(listingid=product_id, user=request.user.username)
        return render(request, "auctions/listing.html", {
            "product": product,
            "added": added,
            "comments": comments
        })

#function to display available categories
@login_required(login_url='/login')
def categories(request):
    return render(request, "auctions/categories.html")


@login_required(login_url='/login')
def category(request, categ):
    # retieving all the products that fall into this category
    category_products = activelistings.objects.filter(category=categ)
    empty = False
    if len(category_products) == 0:
        empty = True
    return render(request, "auctions/category.html", {
        "categ": categ.upper(),
        "empty": empty,
        "products": category_products
    })

#function to close bids
@login_required(login_url='/login')
def closebid(request, product_id):
    winnerobj = Winner()
    listobj = activelistings.objects.get(id=product_id)
    obj = get_object_or_404(bids, listingid=product_id)
    if not obj:
        message = "Deleting Bid"
        msg_type = "danger"
    else:
        bidobj = bids.objects.get(listingid=product_id)
        winnerobj.seller = request.user.username
        winnerobj.winner = bidobj.bidder
        winnerobj.listingid = product_id
        winnerobj.winprice = bidobj.bid_price
        winnerobj.article = bidobj.title
        winnerobj.save()
        message = "Bid Closed"
        msg_type = "success"
        bidobj.delete()
    # removing from watchlist
    if Watchlist.objects.filter(listingid=product_id):
        watchobj = Watchlist.objects.filter(listingid=product_id)
        watchobj.delete()
    # removing from Comment
    if productcomments.objects.filter(listingid=product_id):
        commentobj = productcomments.objects.filter(listingid=product_id)
        commentobj.delete()
    # removing from Listing
    listobj.delete()
    # retrieving the new products list after adding and displaying
    # list of products available in WinnerModel
    winners = Winner.objects.all()
    # checking if there are any products
    empty = False
    if len(winners) == 0:
        empty = True
    return render(request, "auctions/closed.html", {
        "products": winners,
        "empty": empty,
        "message": message,
        "msg_type": msg_type
    })

# view to see closed listings
@login_required(login_url='/login')
def closedlisting(request):
    # list of products available in WinnerModel
    winners = Winner.objects.all()
    # checking if there are any products
    empty = False
    if len(winners) == 0:
        empty = True
    return render(request, "auctions/closedlisting.html", {
        "products": winners,
        "empty": empty
    })