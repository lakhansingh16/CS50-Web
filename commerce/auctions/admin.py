from django.contrib import admin
from .models import User, activelistings,productcomments, Watchlist, Winner

#settings for admin app
class Listingadmin(admin.ModelAdmin):
    list_display=("id","article","seller","Date","Time")


# Register your models here.
admin.site.register(activelistings,Listingadmin)
admin.site.register(User)
admin.site.register(productcomments)
admin.site.register(Watchlist)
admin.site.register(Winner)
