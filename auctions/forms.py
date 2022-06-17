from django.forms import ModelForm
from django import forms
from .models import Auction, Bid, Comment 

# create a new auction listing model form class
class NewListingForm(ModelForm):
    # specifiy the name of model to use
    class Meta:
        model = Auction
        fields = ["title", "description", "starting_bid", "category", "imageURL"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                        "placeholder": "Enter the title of your auction list",
                        "class": "form-control"
                    }
            ),
            "description": forms.Textarea(
                attrs={
                        "placeholder": "Enter the description...",
                        "class": "form-control",
                        "rows": 15
                    }
            ),
            "starting_bid": forms.NumberInput(
                attrs={'class': 'form-control'}
                ),
            "imageURL": forms.URLInput(
                attrs={
                    'class': 'form-control',
                    "placeholder": "Enter the image URL",
                    }
                ) 
        }

# create a new Bid model form class
class NewBidForm(ModelForm):
    # specify the name of model to use
    class Meta:
        model = Bid
        fields = ["bid_price"]

# create a new Comment model from class
class NewCommentForm(ModelForm):
    # sepcifit the name of model to use
    class Meta:
        model = Comment
        fields = ["headline", "message"]
        widgets = {
            "headline": forms.TextInput(
                attrs={
                        "placeholder": "Enter headline",
                        "class": "form-control"
                    }
            ),
            "message": forms.Textarea(
                attrs={
                        "placeholder": "Enter your comment...",
                        "class": "form-control",
                        "rows": 4
                    }
        )}

