import math
from .models import Food_Banks, Shelters, Support_Services
from geopy.geocoders import Nominatim

# Calculates distance between latitude and longitude
def distance_km(lat1, lon1, lat2, lon2):
    R = 6371 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (math.sin(dlat/2)**2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlon/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

geolocator = Nominatim(user_agent="haven_project_code")

def get_point_from_postcode(postcode):
    try:
        # Geocode postcode
        location = geolocator.geocode(postcode)
        if location:
            # Gets latitude and longitude
            print(f"Geocoded {postcode}: {location.latitude}, {location.longitude}")
            return location.latitude, location.longitude
        else:
            print(f"Could not geocode {postcode}")
            return None, None
    except Exception as e:
        print(f"Error geocoding {postcode}: {e}")
        return None, None

# Getting nearest shelters
def get_nearest_shelters(postcode):
        # Gets postcode latitude and longitude
        user_lat, user_lon = get_point_from_postcode(postcode)
          
        if user_lat is None or user_lon is None:
            return[]
        
        # Getting all shelters
        shelters = Shelters.objects.all()
        results = []

        for shelter in shelters:
            if shelter.latitude and shelter.longitude:
                
                # Calculating distance between shelter postcode and user postcode
                dist = distance_km(user_lat, user_lon, shelter.latitude, shelter.longitude)

                if dist < 500:
                        shelter.distance = round(dist, 2)
                        results.append(shelter)

        # Returning nearest shelter in order
        return sorted(results, key=lambda x: x.distance)

# Getting nearest food banks
def get_nearest_food_banks(postcode):
        # Gets postcode latitude and longitude
        user_lat, user_lon = get_point_from_postcode(postcode)
        
        if user_lat is None or user_lon is None:
            return[]
        
        # Getting all food banks
        food_banks = Food_Banks.objects.all()
        results = []

        for food_bank in food_banks:
            if food_bank.latitude and food_bank.longitude:
                # Calculating distance between food bank postcode and user postcode
                dist = distance_km(user_lat, user_lon, food_bank.latitude, food_bank.longitude)

                if dist < 500:
                        food_bank.distance = round(dist, 2)
                        results.append(food_bank)
        
        # Returning nearest shelter in order
        return sorted(results, key=lambda x: x.distance)

# Getting nearest support services
def get_nearest_support_services(postcode):
        # Gets postcode latitude and longitude
        user_lat, user_lon = get_point_from_postcode(postcode)
          
        if user_lat is None or user_lon is None:
            return[]
        
         # Getting all support services
        support_services = Support_Services.objects.all()
        results = []
     
        for support_service in support_services:
            if support_service.latitude and support_service.longitude:
                # Calculating distance between support service postcode and user postcode
                dist = distance_km(user_lat, user_lon, support_service.latitude, support_service.longitude)

                if dist < 500:
                        support_service.distance = round(dist, 2)
                        results.append(support_service)
         # Returning nearest support services in order
        return sorted(results, key=lambda x: x.distance)