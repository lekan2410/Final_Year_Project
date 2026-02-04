from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(City)
admin.site.register(Country)
admin.site.register(Location)
admin.site.register(Support_Services)
admin.site.register(Shelters)
admin.site.register(Food_Banks)
admin.site.register(Review_Support_Service)
admin.site.register(Review_FoodBank)
admin.site.register(Review_Shelter)
