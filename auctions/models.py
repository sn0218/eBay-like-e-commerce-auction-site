from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

    def __str__(self):
        return f"User id: {self.id} | Username: {self.username}"

    def get_username(self):
        return self.username


# define the models of category
class Category(models.Model):
    title = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.title}"


# define the model of a auction list
class Auction(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=512)
    starting_bid = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    current_bid = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="auction_category", blank=True, null=True) # related_name search all the auctions with a given category
    imageURL = models.URLField(blank=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auction_seller")
    closed = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True, null=True)
    # lastBid = models.ForeignKey(Bid, on_delete=models.CASCADE, blank=True, null=True) 

    def __str__(self):
        return f"Auction id: {self.id} | Title: {self.title} | Seller: {self.seller} | Closed: {self.closed}"
    
    def get_fields(self):
        return [(field.name, getattr(self, field.name)) for field in Auction._meta.fields]


# define the model of a bid
class Bid(models.Model):
    bider = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    bid_date = models.DateTimeField(auto_now_add=True)
    bid_price = models.DecimalField(max_digits=9, decimal_places=2)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="auction_bids")

    def __str__(self):
        return f"{self.bider} bid ${self.bid_price} on {self.auction}"


# define the model of a comment
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")
    headline = models.CharField(max_length=64)
    message = models.TextField(blank=False)
    cm_date = models.DateTimeField(auto_now_add=True)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="auction_comments")

    def __str__(self):
        return f"{self.user} comments on {self.auction}"


# define the model of a watchlist
class Watchlist(models.Model):
    auctions = models.ManyToManyField(Auction, related_name="auctions_in_watchlist", blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="watchlist")

    def __str__(self):
        return f"{self.user}'s watchlist"

