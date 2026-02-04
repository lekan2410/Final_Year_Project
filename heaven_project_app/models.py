from django.db import models
from django.contrib.auth.models import User



# Create your models here.

One_Star = 1
Two_Stars = 2
Three_Stars = 3
Four_Stars = 4
Five_Stars = 5


ratings = ((
        One_Star, 'One Star',
        Two_Stars, 'Two Stars',
        Three_Stars, 'Three Stars',
        Four_Stars, 'Four Stars',
        Five_Stars, 'Five Stars'
    ))

cities = ((
    'London', 'England',
    'Rome', 'Italy',
    'Paris', 'France',
    'Barcelona', 'Spain'
))

class Country(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, related_name='cities', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

# location_id (PK), city, country, postcode
class Location(models.Model):
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    post_code = models.CharField(max_length=8)


class Support_Services(models.Model):
    Support_Services_Types = ['Job', 'Job_Support_Services',
                              'Medic', 'Medical_Services',
                              'Safety', 'Saftety_and_Security_Services',
                              'Mental', 'Mental Health Services']

    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    post_code = models.CharField(max_length=8, null=True,
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
    post_code = models.CharField(max_length=8, null=True,
    blank=True)
    category = models.CharField(max_length=200, null=True, blank=True)
    opening_times = models.CharField(max_length=4000, null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    type = models.CharField(max_length=200)
    info = models.CharField(max_length=400)
    real_time_information = models.CharField(max_length=400)


class Food_Banks(models.Model):
    Food_Types = ['Soup', 'Soup Kitchen',
                              'Faith', 'Faith Based Food Bank']

    name = models.CharField(max_length=255)
    city = models.ForeignKey(City, related_name='food_banks', on_delete=models.CASCADE, null=True,
    blank=True)
    country = models.ForeignKey(Country, related_name='food_banks', on_delete=models.CASCADE, null=True,
    blank=True)
    address = models.CharField(max_length=255)
    post_code = models.CharField(max_length=8, null=True,
    blank=True)
    category = models.CharField(max_length=200, null=True, blank=True)
    opening_times = models.CharField(max_length=4000, null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    type = models.CharField(max_length=200)
    info = models.CharField(max_length=400)
    real_time_information = models.CharField(max_length=400)


class Review_Shelter(models.Model):
    shelter_id = models.ForeignKey("Shelters", on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    rating = models.IntegerField(default=One_Star)
    review = models.CharField(max_length=400)


class Review_FoodBank(models.Model):
    foodbank_id = models.ForeignKey("Food_Banks", on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    rating = models.IntegerField(default=One_Star)
    review = models.CharField(max_length=400)

class Review_Support_Service(models.Model):
    support_service_id = models.ForeignKey("Support_Services", on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    rating = models.IntegerField(default=One_Star)
    review = models.CharField(max_length=400)