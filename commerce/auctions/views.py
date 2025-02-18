from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from datetime import datetime

from .models import User, Listing, Comment, Bid

CATEGORIES = ["Home appliances", "Fashion", "Electronics"]

def index(request):
    # Get active listings
    listings = Listing.objects.filter(active="yes")
    return render(request, "auctions/index.html", {
        "listings": listings
    })

# index page for listings of specific category
def cindex(request, cat):
    # active listings
    listings = Listing.objects.filter(active="yes")
    for category in CATEGORIES:
        if cat == category:
            listings = Listing.objects.filter(active="yes", category=cat)
            c = cat

    return render(request, "auctions/cindex.html", {
        "listings": listings,
        "c": c
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

# form for creating a new listing
class NewListingForm(forms.Form):
    title = forms.CharField(label="Title for listing", widget=forms.TextInput(attrs={'style': 'width: 300px;', 'class': 'form-control'}))
    description = forms.CharField(label="Description", widget=forms.TextInput(attrs={'style': 'width: 300px;', 'class': 'form-control'}))
    price = forms.FloatField(label="Price", widget=forms.NumberInput(attrs={'style': 'width: 300px;', 'class': 'form-control'}))
    image = forms.URLField(label="Enter image URL", required=False, widget=forms.URLInput(attrs={'style': 'width: 300px;', 'class': 'form-control'}))
    category = forms.CharField(label="Category", required=False, widget=forms.TextInput(attrs={'style': 'width: 300px;', 'class': 'form-control'}))

@login_required
def create_listing(request):
    if request.method == "POST":

        # current user
        user = request.user
         # Take in the data the user submitted and save it as form
        form = NewListingForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():

            # Isolate the variables from the 'cleaned' version of form data
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            price = form.cleaned_data["price"]
            image = form.cleaned_data["image"]
            category = form.cleaned_data["category"]

            # add new items not the category list if necessary
            if category and category not in CATEGORIES:
                CATEGORIES.append(category)

            #create new bid object
            bid = Bid(
                bid=price,
                bid_by=user
            )
            bid.save()

            #create new listing object
            new_listing =Listing(
                title = title,
                description = description,
                price = bid,
                image_url = image,
                category = category,
                timestamp = datetime.now(),
                listed_by = user
            )
            new_listing.save()

            messages.success(request, 'Listing created successfully.')
            # Redirect user to index
            return HttpResponseRedirect(reverse("index"))

        else:

            # If the form is invalid, re-render the page with existing information.
            messages.error(request, 'Could not create listing, there has been an error.')
            return render(request, "auctions/create.html", {
                "form": form
            })

    else:
        return render(request, "auctions/create.html",{
            "form": NewListingForm()
        })

# Categories page
def category(request):

    return render(request, "auctions/category.html", {
        "categories": CATEGORIES
    })

# page that renders an html for specific listing
def listing(request, listing_id):
    # current user
    user = request.user

    listing = Listing.objects.get(pk=listing_id)
    #check if listing in current user's watchlist
    inwatchlist = user in listing.watchlist.all()

    #check if user is the owner of the listing
    owner = listing.listed_by.username == user.username

    #get all comments on listing
    comments = Comment.objects.filter(listing=listing)
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "watchlist": inwatchlist,
        "comments": comments,
        "owner": owner
    })

# Add listing to watchlist
@login_required
def add(request, listing_id):
    # current user
    user = request.user

    listing = Listing.objects.get(pk=listing_id)
    listing.watchlist.add(user)
    messages.success(request, 'Listing added to watchlist.')
    return HttpResponseRedirect(reverse("listing", args=(listing_id, )))

# remove listing from watchlist
@login_required
def remove(request, listing_id):
     # current user
    user = request.user

    listing = Listing.objects.get(pk=listing_id)
    listing.watchlist.remove(user)
    messages.success(request, 'Listing removed from watchlist.')
    return HttpResponseRedirect(reverse("listing", args=(listing_id, )))

@login_required
def watchlist(request):
    # current user
    user = request.user
    listings = user.userlist.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })

# function for users to add comments on listings
@login_required
def comment(request, listing_id):
    # current user
    user = request.user

    listing = Listing.objects.get(pk=listing_id)
    comment = request.POST['comment']

    new_comment =Comment(
                comment = comment,
                listing = listing,
                timestamp = datetime.now(),
                comment_by = user
            )
    new_comment.save()
    return HttpResponseRedirect(reverse("listing", args=(listing_id, )))

# function for users to place bids on listings
@login_required
def bid(request, listing_id):

    user = request.user
    listing = Listing.objects.get(pk=listing_id)
    if listing.price.bid < float(request.POST['bid']):
        currentbid= Bid(
            bid=request.POST['bid'],
            bid_by=user
        )
        currentbid.save()
        listing.price=currentbid
        listing.save()
        messages.success(request, 'Bid was placed successfully.')
        return HttpResponseRedirect(reverse("listing", args=(listing_id, )))
    else:
        messages.error(request, 'Failed to place bid, make sure your bid is not less than the current price.')
        return HttpResponseRedirect(reverse("listing", args=(listing_id, )))

# function for users to close auction
@login_required
def close(request, listing_id):
    user = request.user
    listing = Listing.objects.get(pk=listing_id)
    listing.active="no"
    listing.save()
    messages.success(request, 'Auction has been closed.')
    if listing.active=="no" and user==listing.price.bid_by:
        messages.success(request, 'Congratulations! you have won the auction')

    return HttpResponseRedirect(reverse("listing", args=(listing_id, )))
