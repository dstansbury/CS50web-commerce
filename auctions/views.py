from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal

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
    print(bids)
    winningBid = bids.filter(isWinningBid = True).first()
    is_watching = UserWatchList.objects.filter(userID=request.user, listingID=listing).exists() if request.user.is_authenticated else False
    #pops the bid_error_message off, so it is only shown on the relevant request, once.
    bid_error_message = request.session.pop("bid_error_message", None)
    # pops the comment_error_message off, so it is only shown on the relevant request, once.
    comment_error_message = request.session.pop("comment_error_message", None)
    
    if listing.currentPrice:
        lowestPossibleBid = listing.currentPrice + Decimal('0.01')
    else:
        lowestPossibleBid = listing.startingBid
    return render(request, "auctions/listing.html", {
        "listing": listing,
        # reversed comments and bids so most recent is shown first
        "comments": reversed(comments),
        "bids": reversed(bids),
        "winningBid": winningBid,
        "is_watching": is_watching,
        "lowestPossibleBid": lowestPossibleBid,
        "bid_error_message": bid_error_message,
        "comment_error_message": comment_error_message
    })

def create(request):
    if request.method == "GET":
        return render(request, "auctions/create.html")

    else:
        newListing = Listings.objects.create(listedBy=request.user,
                                title = request.POST["listingTitle"], 
                                description = request.POST["listingDescription"],
                                startingBid = request.POST["listingStartingBid"],
                                category = request.POST["listingCategory"],
                                imageURL = request.POST["listingImageURL"]
                                )
        newListing.save()
        return redirect(listing, listingID=newListing.listingID)
        


"""
Only accessible if the user is logged in.
Returns a table view of all that users watched items
"""
def watchlist(request):
    user = request.user
    # Check if authentication successful
    if user.is_authenticated:
        userWatchList = user.watchList.all()
        titles = []
        descriptions = []
        print(userWatchList)
        for listing in userWatchList:
            titles.append(listing.title)
            descriptions.append(listing.description)
            print(listing.listingID, listing.title, listing.description)
        return render(request, "auctions/watchlist.html", {
            "userWatchList": userWatchList
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
    for listing in listingsInCategory:
        print(listing.listingID, listing.title, listing.description)
    return render(request, "auctions/listingsInCategory.html", {
        "category": category,
        "listingsInCategory": listingsInCategory
    })

"""
Allows a new bid to be posted into the database.
"""
def new_bid(request, listingID):
    bid_error_message = None
    if request.method == "POST":
        new_bid = Decimal(request.POST["newBid"])
        listing = Listings.objects.get(listingID=listingID)
        bids = Bids.objects.filter(listingID=listingID)
        # check if there are bids
        if bids:
            
            # if yes, update the currentPrice of the listing if the new bid is higher
            if new_bid > listing.currentPrice:
                listing.currentPrice = new_bid
                listing.save()
                # Create a new Bid object and save it to the database
                bid = Bids(listingID=listing, bidValue=new_bid, bidTime=timezone.now(), bidder=request.user)
                bid.save()
            
            # If the new bid is lower, display an error message. Stored in the session
            else:
                request.session['bid_error_message'] = "New bids must exceed the current highest bid."
        
        else:
            # if no bids, check the first bid exceeds the starting price
            if new_bid >= listing.startingBid:
                #if yes, update the current price and save the bid
                listing.currentPrice = new_bid
                listing.save()
                bid = Bids(listingID=listing, bidValue=new_bid, bidTime=timezone.now(), bidder=request.user)
                bid.save()
            
            else:
                # if no, display an error message
                request.session['bid_error_message'] = "Initial bids must be at least as much as the starting price."
        
        return redirect("listing", listingID=listingID)
    
"""
Enables authenticated users to post a comment
"""
def new_comment(request, listingID):
    comment_error_message = None
    if request.method == "POST":
        new_comment = request.POST["new_comment"]
        listing = Listings.objects.get(listingID=listingID)
        checkComments = Comments.objects.filter(listingID=listingID, comment = new_comment)
        # check if the same comment has been made previously to prevent multiple spams of the same comment
        if checkComments.exists():
            request.session['comment_error_message'] = "New comments cannot be identical to previously entered comments, to prevent spam."
        else:
            comment = Comments(listingID=listing, comment=new_comment, commentTime = timezone.now(), userID = request.user)
            comment.save()
        
    return redirect("listing", listingID = listingID)


"""
Enables users to close auctions that they listed
"""
def close_listing(request, listingID):
    if request.method == "POST":
        listing = Listings.objects.get(listingID=listingID)
        listing.listingActive = False
        listing.save()
        winningBid = Bids.objects.filter(listingID=listingID).order_by('bidValue').last()
        winningBid.isWinningBid = True
        winningBid.save()
    
    return redirect("listing", listingID=listingID)