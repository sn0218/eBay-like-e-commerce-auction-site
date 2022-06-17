from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("listing/<int:auction_id>", views.listing, name="listing"),
    path("listing/<int:auction_id>/bid", views.bid, name="bid"),
    path("listing/<int:auction_id>/close", views.close, name="close"),
    path("listing/<int:auction_id>/comment", views.comment, name="comment"),
    path("listing/<int:auction_id>/addWatchlist", views.addWatchlist, name="addWatchlist"),
    path("listing/<int:auction_id>/removeWatchlist", views.removeWatchlist, name="removeWatchlist"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:category_id>", views.category, name="category"),
    path("watchlist", views.watchlist, name="watchlist")
]
