from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Bid(models.Model):
    bid = models.FloatField(default=0)
    bid_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")



class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=100)
    price = models.ForeignKey(Bid, on_delete=models.CASCADE, blank=True, null=True, related_name="bidprice")
    image_url = models.URLField(blank=True, null=True)
    active = models.CharField(max_length=64, default="yes")
    category = models.CharField(max_length=64, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    listed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")
    watchlist = models.ManyToManyField(User, blank=True, null=True, related_name="userlist")

    def __str__(self):
        return f"{self.title}"

class Comment(models.Model):
    comment = models.CharField(max_length=300)
    comment_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="item")
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return f"comment on item,{self.listing}, by {self.comment_by}"

