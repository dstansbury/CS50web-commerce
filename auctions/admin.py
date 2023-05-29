from django.contrib import admin

from .models import User, Listings, UserWatchList, Bids, Comments

# Register your models here.
admin.site.register(User)
admin.site.register(Listings)
admin.site.register(UserWatchList)
admin.site.register(Bids)
admin.site.register(Comments)
