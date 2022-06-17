from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Auction, Bid, Category, Comment, Watchlist
from .forms import NewCommentForm, NewListingForm, NewBidForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist


def index(request):
    return render(request, "auctions/index.html", {
        "auctions": Auction.objects.filter(closed=False).order_by('-creation_date')
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
            # return sucessful message
            messages.success(request, f'Welcome, {username}. Login successfully.')

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


def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all()
    })


def category(request, category_id):
    try:
        # get a list of all active listing of the category
        auctions = Auction.objects.filter(category=category_id, closed=False).order_by('-creation_date')
         
    except Auction.DoesNotExist:
        return render(request, "auctions/error.html", {
            "code": 404,
            "message": f"The category does not exist."
        })
   
    try:
        # get the category
        category = Category.objects.get(pk=category_id)

    except Category.DoesNotExist:
        return render(request, "auctions/error.html", {
            "code": 404,
            "message": f"The category does not exist."
        })

    return render(request, "auctions/category.html", {
        "auctions": auctions,
        "category": category
    })


@login_required(login_url="login") 
def watchlist(request):
    # check the existance of the user's watchlist
    try:
        watchlist = Watchlist.objects.get(user=request.user)
        auctions = watchlist.auctions.all().order_by('-id')
        # calculate the number of items in the watchlist
        watchingNum = watchlist.auctions.all().count()

    except ObjectDoesNotExist:
        # if watchlist does not exist
        watchlist = None
        auctions = None
        watchingNum = 0
    

    return render(request, "auctions/watchlist.html", {
        # return the listings in the watchlist
        "watchlist": watchlist,
        "auctions": auctions,
        "watchingNum": watchingNum
    })


@login_required(login_url="login")
def create(request):
    # check the request method is POST
    if request.method == "POST":
        # create a form instance with POST data
        form = NewListingForm(request.POST, request.FILES)

        # check whether it's valid
        if form.is_valid():
            # save the form from data to model
            new_listing = form.save(commit=False)
            # save the request user as seller
            new_listing.seller = request.user
            # save the starting bid as current price
            new_listing.current_bid = form.cleaned_data['starting_bid']
            new_listing.save()

            # return sucessful message
            messages.success(request, 'Create the auction listing successfully.')

            # redirect the user to the index page
            return HttpResponseRedirect(reverse("index"))

        else:
            form = NewListingForm()

            # if the form is invalid, re-render the page with existing information
            messages.error(request, 'The form is invalid. Please resumbit.')
            return render(request, "auctions/create.html", {
                "form": form
            })
    
    # if the request method is GET
    else:
        form = NewListingForm()
        return render(request, "auctions/create.html", {
            "form": form
        })


def listing(request, auction_id):  
    try:
        # get the auction listing by id
        auction = Auction.objects.get(pk=auction_id)
        
    except Auction.DoesNotExist:
        return render(request, "auctions/error.html", {
            "code": 404,
            "message": "The auction does not exist."
        })

    # set watching flag be False as default
    watching = False
    # set the highest bidder is None as default    
    highest_bidder = None

    # check if the auction in the watchlist
    if request.user.is_authenticated and Watchlist.objects.filter(user=request.user, auctions=auction):
        watching = True
    
    # get the page request user
    user = request.user

    # get the number of bids
    bid_Num = Bid.objects.filter(auction=auction_id).count()

    # get all comments of the auction
    comments = Comment.objects.filter(auction=auction_id).order_by("-cm_date")

    # get the highest bids of the aunction
    highest_bid = Bid.objects.filter(auction=auction_id).order_by("-bid_price").first()
    
    # check the request method is POST
    if request.method == "GET":
        form = NewBidForm()
        commentForm = NewCommentForm()

        # check if the auction listing is not closed
        if not auction.closed:
            return render(request, "auctions/listing.html", {
            "auction": auction,
            "form": form,
            "user": user,
            "bid_Num": bid_Num,
            "commentForm": commentForm,
            "comments": comments,
            "watching": watching
            }) 

        # the auction is closed
        else:
            # check the if there is bid for the auction listing
            if highest_bid is None:
                messages.info(request, 'The bid is closed and no bidder.')

                return render(request, "auctions/listing.html", {
                    "auction": auction,
                    "form": form,
                    "user": user,
                    "bid_Num": bid_Num,
                    "highest_bidder": highest_bidder,
                    "commentForm": commentForm,
                    "comments": comments,
                    "watching": watching
                })

            else:
                # assign the highest_bidder
                highest_bidder = highest_bid.bider

                # check the request user if the bid winner    
                if user == highest_bidder:
                    messages.info(request, 'Congratulation. You won the bid.')
                else:
                    messages.info(request, f'The winner of the bid is {highest_bidder.username}')

                return render(request, "auctions/listing.html", {
                "auction": auction,
                "form": form,
                "user": user,
                "highest_bidder": highest_bidder,
                "bid_Num": bid_Num,
                "commentForm": commentForm,
                "comments": comments,
                "watching": watching
                })

    
    # listing itself does not support POST method
    else:
        return render(request, "auctions/error.html", {
            "code": 405,
            "message": "The POST method is not allowed."
        })
        
        

@login_required(login_url="login")
def close(request, auction_id):
    # check to handle POST method only
    if request.method == "POST":
        # check the existence auction
        try:
            # get the auction listing by id
            auction = Auction.objects.get(pk=auction_id)

        except Auction.DoesNotExist:
            return render(request, "auctions/error.html", {
                "code": 404,
                "message": "The auction does not exist."
            })

        # check whether the request user who create the listing
        if request.user != auction.seller:
            messages.error(request, 'The request is not allowed.')
            return HttpResponseRedirect(reverse("listing", args=(auction.id,)))

        else:
            # update and save the closed status
            auction.closed = True
            auction.save()
            
            # pop up the message
            messages.success(request, 'The auction listing is closed sucessfully.')
            return HttpResponseRedirect(reverse("listing", args=(auction.id,)))

    # close view not support GET method    
    else:
        return render(request, "auctions/error.html", {
            "code": 405,
            "message": "The GET method is not allowed."
        })
        

@login_required(login_url="login")
def bid(request, auction_id):  
    # check to handle POST method only
    if request.method == "POST":
        # check the existence auction
        try:
            # get the auction listing by id
            auction = Auction.objects.get(pk=auction_id)     
            
        except Auction.DoesNotExist:
            return render(request, "auctions/error.html", {
                "code": 404,
                "message": "The auction does not exist."
            })

        # get the highest bid of the aunction
        highest_bid = Bid.objects.filter(auction=auction_id).order_by("-bid_price").first()

        # check if there is any bid
        if highest_bid is None:
            highest_bid_price = auction.current_bid
        else:
            highest_bid_price = highest_bid.bid_price

        # create a form instance with POST data
        form = NewBidForm(request.POST, request.FILES)

        # check the auction if it is closed
        if auction.closed is True:
            messages.error(request, 'The auction listing is closed.')
            return HttpResponseRedirect(reverse("listing", args=(auction.id,))) 
        
        # the auction list is active
        else:
            # check whether it's valid
            if form.is_valid():
                # isolate contemt from the clean version of form data
                bid_price = form.cleaned_data["bid_price"]

                # validate the bid offer
                if bid_price > auction.starting_bid and bid_price > (auction.current_bid or highest_bid_price):
                    # save the form from data to model
                    new_bid = form.save(commit=False)
                    # save the request user as bider
                    new_bid.bider = request.user
                    # get and save the auction
                    new_bid.auction = auction
                    new_bid.save()

                    # update and save the current price
                    auction.current_bid = bid_price
                    auction.save()

                    # return sucessful message
                    messages.success(request, 'Your Bid offer is made successfully.')

                # handle invalid bid offer
                else:
                    #if the bid is invalid, populate the msg
                    messages.error(request, 'Please submit a valid bid offer. Your bid offer must be higher than the starting bid and current price.')

                # valid form, redirect the user to the listing page 
                return HttpResponseRedirect(reverse("listing", args=(auction.id,)))    

            else:
                # if the form is invalid, re-render the page with existing information
                messages.error(request, 'Please submit a valid bid offer. Your bid offer must be higher than the starting bid and current price.')

                # redirect the user to the listing page
                return HttpResponseRedirect(reverse("listing", args=(auction.id,)))
    
    # bid view do not support get method
    else:
        return render(request, "auctions/error.html", {
            "code": 405,
            "message": "The GET method is not allowed."
        })


@login_required(login_url="login")
def comment(request, auction_id):
    # check to handle POST method only
    if request.method == "POST":

        # check the existence auction
        try:
            # get the auction listing by id
            auction = Auction.objects.get(pk=auction_id)     
            
        except Auction.DoesNotExist:
            return render(request, "auctions/error.html", {
                "code": 404,
                "message": "The auction does not exist."
            })
            
        # create a form instance with POST data
        form = NewCommentForm(request.POST, request.FILES)

        # check whether it's valid
        if form.is_valid():
            # save the comment from from data to model
            new_comment = form.save(commit=False)
            # save the request user who leaves the comment
            new_comment.user = request.user
            # save the auction for this comment
            new_comment.auction = auction
            new_comment.save()

            # return sucessful message
            messages.success(request, 'Your comment is received sucessfully.')

            return HttpResponseRedirect(reverse("listing", args=(auction.id,)))
        
        # handle invalid comment form
        else:
            # if the form is invalid
            messages.error(request, 'Please submit a valid comment.')
     
    # comment view do not support get method
    else:
        return render(request, "auctions/error.html", {
            "code": 405,
            "message": "The GET method is not allowed."
        })


@login_required(login_url="login")
def addWatchlist(request, auction_id):   
    # check to handle POST method only
    if request.method == "POST":
        # check the existence auction
        try:
            # get the auction listing by id
            auction = Auction.objects.get(pk=auction_id)     
            
        except Auction.DoesNotExist:
            return render(request, "auctions/error.html", {
                "code": 404,
                "message": "The auction does not exist."
            })

        # check the existance of the user's watchlist
        try:
            watchlist = Watchlist.objects.get(user=request.user)

        except ObjectDoesNotExist:
            # if no watchlist, create an watchlist object for the user
            watchlist = Watchlist.objects.create(user=request.user)
        
        # check if the item exists in the user's watchlist
        if Watchlist.objects.filter(user=request.user, auctions=auction):
            messages.error(request, 'You already added in your watchlist')
            return HttpResponseRedirect(reverse("listing", args=(auction.id,)))

        # if the item is not in the watchlist
        watchlist.auctions.add(auction)
            
        # return sucessful message
        messages.success(request, 'The listing is added to your Watchlist.')

        return HttpResponseRedirect(reverse("listing", args=(auction.id,)))
        
     
    # addWatchlist view do not support get method
    else:
        return render(request, "auctions/error.html", {
            "code": 405,
            "message": "The GET method is not allowed."
        })


@login_required(login_url="login")
def removeWatchlist(request, auction_id):   
    # check to handle POST method only
    if request.method == "POST":
        # check the existence auction
        try:
            # get the auction listing by id
            auction = Auction.objects.get(pk=auction_id)     
            
        except Auction.DoesNotExist:
            return render(request, "auctions/error.html", {
                "code": 404,
                "message": "The auction does not exist."
            })
        
        # check if the item exists in the user's watchlist
        if Watchlist.objects.filter(user=request.user, auctions=auction):
            # get the user's watchlist
            watchlist = Watchlist.objects.get(user=request.user)
           
            # delete the auction from the users watchlist
            watchlist.auctions.remove(auction)
                
            # return sucessful message
            messages.success(request, 'The listing is removed from your watchlist.')

            return HttpResponseRedirect(reverse("listing", args=(auction.id,)))
        
        else:
            # return error message
            messages.success(request, 'You cannot remove the listing not in your watchlist.')

            return HttpResponseRedirect(reverse("listing", args=(auction.id,)))
   
     
    # removeWatchlist view do not support get method
    else:
        return render(request, "auctions/error.html", {
            "code": 405,
            "message": "The GET method is not allowed."
        })










