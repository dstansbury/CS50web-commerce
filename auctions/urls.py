from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name = "create"),
    path("watchlist", views.watchlist, name = "watchlist"),
    path("add_to_watchlist", views.add_to_watchlist, name="add_to_watchlist"),
    path("remove_from_watchlist", views.remove_from_watchlist, name="remove_from_watchlist"),
    path("categories", views.categories, name = "categories"),
    path("categories/<str:category>", views.listingsInCategory, name = "listingsInCategory"),
    path("listing/<int:listingID>", views.listing, name="listing"),
    path("new_bid/<int:listingID>", views.new_bid, name="new_bid"),
    path("new_comment/<int:listingID>", views.new_comment, name="new_comment"),
    path("close_listing/<int:listingID>", views.close_listing, name="close_listing")
]
