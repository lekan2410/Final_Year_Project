import csv
from heaven_project_app.models import (Country, City, Location, Shelters, Food_Banks, Support_Services)
from django.core.management.base import BaseCommand


# from heaven_project_app.models import (
#     Country, City,
#     Food_Banks, Shelters, Support_Services
# )

# Food_Banks.objects.all().delete()
# Shelters.objects.all().delete()
# Support_Services.objects.all().delete()
# City.objects.all().delete()
# Country.objects.all().delete()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        with open('homeless-geo-v3.csv', 'r', encoding='latin-1') as file:
            reader = csv.DictReader(file)
            
            country, _ = Country.objects.get_or_create(
                    name = "England"
            )

            for row in reader:
                 
                city, _ = City.objects.get_or_create(name = row['City'].strip(),
                country=country)

                category = row['Category'].lower().strip()
                
                if category == "food":
                    
                    Food_Banks.objects.get_or_create(
                        name=row['Name'],
                        defaults = {
                                "address" : row['Street'],
                                "city" : city,
                                "country" : country,
                                "post_code" : row['Postcode'],
                                "phone_number" : row.get('Phone', ''),
                                "category" : category,
                                "type" : "Food Bank",
                                "opening_times" : row["Opening_times"],
                                "info" : row['Notes'],
                                "real_time_information" : ""
                            
                        }
                    )

                    
                

                elif 'shelter' in category or 'homeless' in category or 'community' in category:
                        Shelters.objects.get_or_create(
                            name=row['Name'],
                            defaults = {
                                        "address" : row['Street'],
                                        "city" : city,
                                        "country" : country,
                                        "post_code" : row['Postcode'],
                                        "phone_number" : row.get('Phone', ''),
                                        "type" : 'Shelters',
                                        "category" : category,
                                        "opening_times" : row["Opening_times"],
                                        "info" : row['Notes'],
                                        "real_time_information" : "",
                                
                                }
                        )
                
                
                else: 
                     Support_Services.objects.get_or_create(
                        name=row['Name'],
                        defaults={
                            "address": row['Street'],
                            "city": city,
                            "country": country,
                            "post_code": row['Postcode'],
                            "phone_number": row.get('Phone', ''),
                            "type": "Support Service",
                            "category": category,
                            "opening_times": row["Opening_times"],
                            "info": row['Notes'],
                            "real_time_information": ""
                        }
                    )
                    
                    
                    



    
    
                
                

