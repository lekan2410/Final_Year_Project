import csv
from heaven_project_app.models import (Country, City, Location, Shelters, Food_Banks, Support_Services)
from django.core.management.base import BaseCommand



# Food_Banks.objects.all().delete()
# Shelters.objects.all().delete()
# Support_Services.objects.all().delete()
# City.objects.all().delete()
# Country.objects.all().delete()


# Command Function
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Reading File
        with open('homeless-geo-v3.csv', 'r', encoding='latin-1') as file:
            reader = csv.DictReader(file)
            
            country, _ = Country.objects.get_or_create(
                    name = "England"
            )
            
            # Reading each row in the file
            for row in reader:
                 
                # Getting City row.
                city, _ = City.objects.get_or_create(name = row['City'].strip(),
                country=country)
                
                # Getting Category
                category = row['Category'].lower().strip()
                
                # Creating food banks if category is related to Food Bank
                if category == "food":
                    
                    Food_Banks.objects.get_or_create(
                        name=row['Name'],
                        defaults = {
                                "address" : row['Street'],
                                "city" : city,
                                "country" : country,
                                "postcode" : row['Postcode'],
                                "phone_number" : row.get('Phone', ''),
                                "category" : category,
                                "type" : "Food Bank",
                                "opening_times" : row["Opening_times"],
                                "info" : row['Notes'],
                                "real_time_information" : ""
                            
                        }
                    )

                    
                
                # Creating shelters if category is related to Shelter
                elif 'shelter' in category or 'homeless' in category or 'community' in category:
                        Shelters.objects.get_or_create(
                            name=row['Name'],
                            defaults = {
                                        "address" : row['Street'],
                                        "city" : city,
                                        "country" : country,
                                        "postcode" : row['Postcode'],
                                        "phone_number" : row.get('Phone', ''),
                                        "type" : 'Shelters',
                                        "category" : category,
                                        "opening_times" : row["Opening_times"],
                                        "info" : row['Notes'],
                                        "real_time_information" : "",
                                
                                }
                        )
                
                # Creating support services
                else: 
                     Support_Services.objects.get_or_create(
                        name=row['Name'],
                        defaults={
                            "address": row['Street'],
                            "city": city,
                            "country": country,
                            "postcode": row['Postcode'],
                            "phone_number": row.get('Phone', ''),
                            "type": "Support Service",
                            "category": category,
                            "opening_times": row["Opening_times"],
                            "info": row['Notes'],
                            "real_time_information": ""
                        }
                    )
                    
                    
                    



    
    
                
                

