from django.contrib.auth.models import AbstractUser
from django.db import models

#Predefined model for users data
class User(AbstractUser):
    pass


#Model for the active listinggs on the website
class activelistings(models.Model):
    article = models.CharField(max_length=64)
    seller = models.CharField(max_length=64)
    category = models.CharField(max_length=64)
    Date = models.DateField(auto_now_add=True)
    Time = models.TimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField()
    photo_link = models.CharField(max_length=1024,default=None, blank=True, null=True)

#Model for bids on every article
class bids(models.Model):
    bidder = models.CharField(max_length=64,blank=True)
    title = models.CharField(max_length=64)
    listingid = models.IntegerField()
    bid_price = models.DecimalField(max_digits=5, decimal_places=2)



#Model for comments on bids and articles on sale
class productcomments(models.Model):
    person = models.CharField(max_length=64)
    comment = models.CharField(max_length=64)
    listingid = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

#Model for listings in watchlist of every user
class Watchlist(models.Model):
    user = models.CharField(max_length=64)
    listingid = models.IntegerField()


# model to store the winners
class Winner(models.Model):
    seller = models.CharField(max_length=64)
    winner = models.CharField(max_length=64)
    listingid = models.IntegerField()
    winprice = models.DecimalField(max_digits=5, decimal_places=2)
    article = models.CharField(max_length=64, null=True)