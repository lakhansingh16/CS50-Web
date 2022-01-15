from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("active_listings",views.active_listings, name="active_listings"),
    path("create",views.create_listing,name="create_listing"),
    path("listing/<int:product_id>",views.listing,name="listing"),
    path("addcomment/<int:product_id>",views.addcomment, name="addcomment"),
    path("addtowatchlist/<int:product_id>",views.addtowatchlist, name="addtowatchlist"),
    path("categories", views.categories, name="categories"),
    path("category/<str:categ>", views.category, name="category"),
    path("closebid/<int:product_id>", views.closebid, name="closebid"),
    path("closedlistings",views.closedlisting, name="closedlisting"),
]
