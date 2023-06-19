from django.contrib.auth.models import AbstractUser
from django.db import models


"""
Defines the User table in the DB. It uses the default Django User model.
"""
class User(AbstractUser):
    #blank = True so that the user can have no items they are watching
    watchList = models.ManyToManyField('Listings', through='UserWatchList', blank=True, related_name="watchList")
    
    def __str__(self):
        return f"{self.username}"

"""
Defines the listings table in the DB.
"""
class Listings(models.Model):
    listingID = models.AutoField(primary_key=True, null=False)
    title = models.CharField(max_length=64, null=False, blank=False)
    description = models.CharField(max_length=256, null=False, blank=False)
    startingBid = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    currentPrice = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    #intention with the null=True is to allow for a null entry in the DB
    #intention with blank=True is to allow for a blank field in the form
    category = models.CharField(max_length=64, null=True, blank=True)
    imageURL = models.CharField(max_length=1000, null=True, blank=True)
    #blank = true so that the listing can have no watchers
    watchers = models.ManyToManyField(User, through='UserWatchList', blank = True, related_name="watchers")
    listedBy = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listedBy", null=False, blank=False)
    listedTime = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    listingActive = models.BooleanField(default = True, null = False, blank = False)

    def __str__(self):
        return f"{self.listingID}: {self.title}"

"""
Defines the watchlist table in the DB. It is many to many. 
A user can be watching many items and an item can be watched by many users.
"""
class UserWatchList(models.Model):
    watchListID = models.AutoField(primary_key=True, null=False)
    userID = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userWatchList")
    listingID = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="userWatchList")

    def __str__(self):
        return f"{self.watchListID}: user {self.userID}"

"""
Defines the Bids table in the DB. It is a one to many relationship. Each bid is associated with one listing. 
Each listing can have multiple bids.
"""
class Bids(models.Model):
    bidID = models.AutoField(primary_key=True, null=False)
    listingID= models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="listingBids")
    bidValue = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    bidTime = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    isWinningBid = models.BooleanField(default = False, null = False, blank = False)

    def __self__(self):
        return f"{self.bidID}: value {self.bidValue}"
"""
Defines the comments table in the DB. It is a one to many relationship. 
A user can have many comments on many listings but a comment can only have one user and one listing.
"""
class Comments(models.Model):
    commentID = models.AutoField(primary_key=True, null=False)
    userID = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userComments", null=False, blank=False)
    listingID = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="listingComments", null=False, blank=False)
    #intention with the null=True is to allow for a null entry in the DB
    #intention with blank=True is to allow for a blank field in the form
    comment = models.CharField(max_length=512, null=True, blank=True)
    commentTime= models.DateTimeField(auto_now_add=True, null=False, blank=False)

    def __self__(self):
        return f"{self.commentID}: user {self.userID}, listing {self.listingID}, saying {self.comment}"
