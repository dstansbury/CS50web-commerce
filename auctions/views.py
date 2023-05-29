from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listings, UserWatchList, Bids, Comments


def index(request):
    listings = Listings.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings
    })


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
    
def listing(request, listingID):
    listing = Listings.objects.get(listingID=listingID)
    comments = Comments.objects.filter(listingID=listingID)
    bids = Bids.objects.filter(listingID=listingID)
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": comments,
        "bids": bids
    })

def create(request):
    pass

"""
Only accessible if the user is logged in.
Returns a table view of all that users watched items
"""
def watchlist(request):
    # Check if authentication successful
    if request.user.is_authenticated:
        return render(request, "auctions/watchlist.html", {
            "watchlist": watchlist
        })
    else:
        return render(request, "auctions/login.html", {
            "message": "Log in to be able to view your watchlist."
        })

"""
Table view of all the categories
"""
def categories(request):
    return render(request, "auctions/categories.html")

"""
Table view of all the listings in a given category
"""
def listingsInCategory(request, category):
    return render(request, "auctions/listingsInCategory.html", {
        "category": category.capitalize()
    })