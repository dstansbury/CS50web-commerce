from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
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
    is_watching = UserWatchList.objects.filter(userID=request.user, listingID=listing).exists() if request.user.is_authenticated else False
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": comments,
        "bids": bids,
        "is_watching": is_watching
    })

def create(request):
    return render(request, "auctions/create.html")

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
Adds an item to a user's watchlist if they are not watching it already.
"""
def add_to_watchlist(request):
    if request.method == "POST":
        listingID = request.POST["listingID"]
        user = request.user

        if user.is_authenticated and not user.watchList.filter(listingID=listingID).exists():
            listing = Listings.objects.get(listingID=listingID)
            UserWatchList.objects.create(userID=user, listingID=listing)

    return redirect("listing", listingID=listingID)

def remove_from_watchlist(request):
    if request.method == "POST":
        listingID = request.POST["listingID"]
        user = request.user

        if user.is_authenticated and user.watchList.filter(listingID=listingID).exists():
            listing = Listings.objects.get(listingID = listingID)
            UserWatchList.objects.filter(userID=user, listingID=listing).delete()
            
    return redirect("listing", listingID=listingID)
"""
List view of all the categories, sorted alphabetically
"""
def categories(request):
    categories = Listings.objects.values_list('category', flat=True).distinct().order_by('category')
    return render(request, "auctions/categories.html", {
        "categories": categories
    })

"""
Table view of all the listings in a given category
"""
def listingsInCategory(request, category):
    listingsInCategory = Listings.objects.filter(category=category)
    return render(request, "auctions/listingsInCategory.html", {
        "category": category,
        "listingsInCategory": listingsInCategory
    })