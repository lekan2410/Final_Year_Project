from django.db import models
from django.contrib.auth.models import User
import time
from geopy.geocoders import Nominatim



# Create your models here.
One_Star = 1
Two_Stars = 2
Three_Stars = 3
Four_Stars = 4
Five_Stars = 5


geolocator = Nominatim(
    user_agent="heaven_services_locator_v1",
    timeout=10)

star_choices = [
        ("1", '⭐'),
        ("2", '⭐⭐'),
        ("3", '⭐⭐⭐'),
        ("4", '⭐⭐⭐⭐'),
        ("5", '⭐⭐⭐⭐⭐'),
    ]


YES_NO_CHOICES = [
    ("1", "Yes"),
    ("0", "No")
]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to="profile_images/", blank=True)

    def __str__(self):
        return self.user.username

class Country(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, related_name='cities', on_delete=models.CASCADE)

    def __str__(self):
        return self.name



class Support_Services(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    postcode = models.CharField(max_length=8, null=True,
    blank=True)
    phone_number = models.CharField(max_length=20)
    city = models.ForeignKey(City, related_name='support_services', on_delete=models.CASCADE, null=True,
    blank=True)
    country = models.ForeignKey(Country, related_name='support_services', on_delete=models.CASCADE, null=True,
    blank=True)
    opening_times = models.CharField(max_length=4000, null=True, blank=True)
    category = models.CharField(max_length=200, null=True, blank=True)
    type = models.CharField(max_length=200)
    info = models.CharField(max_length=400)
    real_time_information = models.CharField(max_length=400)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.postcode and (not self.latitude or not self.longitude):
            try:
                location = geolocator.geocode(self.postcode)

                if location:
                    self.latitude = location.latitude
                    self.longitude = location.longitude
                    print(f"✅ Geocoded {self.postcode}")

                else:
                    print(f"❌ Could not geocode {self.postcode}")

                time.sleep(1)  # 🔥 prevent rate limiting

            except Exception as e:
                print(f"⚠️ Error: {e}")

        super().save(*args, **kwargs)

# https://plainenglish.io/blog/importing-csv-data-into-django-models

class Shelters(models.Model):
    Shelters_Types = ['Specialised', 'Specialised_Centre',
                              'Day', 'Day_Shelter/Centre',
                              'Safety', 'Saftety_and_Security_Services',
                              'Mental', 'Mental Health Services']

    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.ForeignKey(City, related_name='shelters', on_delete=models.CASCADE, null=True,
    blank=True)
    country = models.ForeignKey(Country, related_name='shelters', on_delete=models.CASCADE, null=True,
    blank=True)
    postcode = models.CharField(max_length=8, null=True,
    blank=True)
    
    category = models.CharField(max_length=200, null=True, blank=True)
    opening_times = models.CharField(max_length=4000, null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    type = models.CharField(max_length=200)
    info = models.CharField(max_length=400)
    real_time_information = models.CharField(max_length=400)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)


    def save(self, *args, **kwargs):
        if self.postcode and (not self.latitude or not self.longitude):
            try:
                location = geolocator.geocode(self.postcode)

                if location:
                    self.latitude = location.latitude
                    self.longitude = location.longitude
                    print(f"✅ Geocoded {self.postcode}")

                else:
                    print(f"❌ Could not geocode {self.postcode}")

                time.sleep(1)  # 🔥 prevent rate limiting

            except Exception as e:
                print(f"⚠️ Error: {e}")

        super().save(*args, **kwargs)


class Food_Banks(models.Model):
    name = models.CharField(max_length=255)
    city = models.ForeignKey(City, related_name='food_banks', on_delete=models.CASCADE, null=True,
    blank=True)
    country = models.ForeignKey(Country, related_name='food_banks', on_delete=models.CASCADE, null=True,
    blank=True)
    address = models.CharField(max_length=255)
    postcode = models.CharField(max_length=8, null=True,
    blank=True)
    
    category = models.CharField(max_length=200, null=True, blank=True)
    opening_times = models.CharField(max_length=4000, null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    type = models.CharField(max_length=200)
    info = models.CharField(max_length=400)
    
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)


    def save(self, *args, **kwargs):
        if self.postcode and (not self.latitude or not self.longitude):
            try:
                location = geolocator.geocode(self.postcode)

                if location:
                    self.latitude = location.latitude
                    self.longitude = location.longitude
                    print(f"✅ Geocoded {self.postcode}")

                else:
                    print(f"❌ Could not geocode {self.postcode}")

                time.sleep(1)  # 🔥 prevent rate limiting

            except Exception as e:
                print(f"⚠️ Error: {e}")

        super().save(*args, **kwargs)


class Review_Shelter(models.Model):
    shelter_id = models.ForeignKey("Shelters", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.CharField(choices=star_choices, max_length=20, null=True, blank=True)
    easy_access_q = models.CharField(choices=YES_NO_CHOICES, null=True, blank=True, max_length=4)
    staff_q = models.CharField(choices=YES_NO_CHOICES, null=True, blank=True, max_length=4)
    recommend_q = models.CharField(choices=YES_NO_CHOICES, null=True, blank=True, max_length=4)

class Review_FoodBank(models.Model):
    foodbank_id = models.ForeignKey("Food_Banks", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.CharField(choices=star_choices, max_length=20, null=True, blank=True)
    easy_access_q = models.CharField(choices=YES_NO_CHOICES, null=True, blank=True, max_length=4)
    staff_q = models.CharField(choices=YES_NO_CHOICES, null=True, blank=True, max_length=4)
    recommend_q = models.CharField(choices=YES_NO_CHOICES, null=True, blank=True, max_length=4)
 

class Review_Support_Service(models.Model):
    support_service_id = models.ForeignKey("Support_Services", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.CharField(choices=star_choices, max_length=20, null=True, blank=True)
    easy_access_q = models.CharField(choices=YES_NO_CHOICES, null=True, blank=True, max_length=4)
    staff_q = models.CharField(choices=YES_NO_CHOICES, null=True, blank=True, max_length=4)
    recommend_q = models.CharField(choices=YES_NO_CHOICES, null=True, blank=True, max_length=4)
