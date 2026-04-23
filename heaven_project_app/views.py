from django.utils import timezone
from datetime import timedelta
import os

from django.views.generic import DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .utils import *
from .chatbot import RuleBasedChatbot, pairs
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import *
from django.db.models import Q
from .forms import *
from .models import *
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests


# Create your views here.

#Login View
def login_view(request):
     if request.method == "POST":
          form = AuthenticationForm(request, data=request.POST)

         # Checking if form is valid
          if form.is_valid():
               user = form.get_user()
               
               if not user.is_active:
                    form.add_error(None, "Email not verified. Check your inbox" )
               else:
                    login(request, user) 
                    return redirect("/")
          
           
     else:
          form = AuthenticationForm()
     
     
     
     return render(request, "heaven_project_code/login_register/login.html", {"form" : form} )


# Logout view
def logout_view(request): 
     logout(request)

     return render(request,  "heaven_project_code/home/home.html" )
     
# Deletes Account
def delete_account(request):
     if request.method == "POST":
          user = request.user
          logout(request)
          user.delete()
     
     return redirect("login")

# Register View
def register(request):

     # Set threshold to 20 minutes ago
     threshold = timezone.now() - timedelta(minutes=20)
     # Delete inactive users older than 20 minutes
     User.objects.filter(is_active=False, date_joined__lt=threshold).delete()
    
     # Checks if user is logged in
     if request.user.is_authenticated:
          logout(request)
     
      
     if request.method =="POST":
          form = RegisterForm(request.POST)
           
          # Checking if form is valid
          if form.is_valid():
               user = form.save()
               user.is_active = False
               user.save()
               
               # Generating verification link
               token = default_token_generator.make_token(user)
               uid = urlsafe_base64_encode(force_bytes(user.pk))
               current_site = get_current_site(request)
               verification_link = f"http://{current_site.domain}/verify-email/{uid}/{token}"
               
                # Sending email to user
               send_mail(
                    'Verify your email',
                    f'Click this link to verify your account: {verification_link}',
                    'noreply@havenproject.com',
                    [user.email],
                    fail_silently=False
               )

               return render(request, "heaven_project_code/login_register/verify_email.html")
          
     else: 
          form = RegisterForm()



     return render(request, "heaven_project_code/login_register/register.html", {"form" : form})


 # verifying user email
def verify_email(request, uidb64, token):
     try:
           # decoding user id
          uid = urlsafe_base64_decode(uidb64).decode()
          user = User.objects.get(pk=uid)
     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
          user = None
     
      # Checking user and token are valid and saves user in database
     if user and default_token_generator.check_token(user, token):
          user.is_active = True
          user.save()
          return redirect('login')
     else:
          return HttpResponse("Invalid or expired verification link")


 # Forgotten Password Form
def enter_email_verification(request):
     if request.method =="POST":
          form = EmailVerifcationForm(request.POST)
          
           # Checking if form is valid
          if form.is_valid():

               try:
                    # Getting email from form
                    email = form.cleaned_data['email']
                    
                    # Getting user that has the email and generating verification link
                    user = User.objects.get(email=email)
                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    current_site = get_current_site(request)
                    verification_link = f"http://{current_site.domain}/verify_email_password_reset/{uid}/{token}"
                    
                    # Sending email to user
                    send_mail(
                         'Verify your email',
                         f'Click this link to verify your account: {verification_link}',
                         'noreply@havenproject.com',
                         [user.email],
                         fail_silently=False
                    )
               except User.DoesNotExist:
                     return HttpResponse("The email address you entered is not associated with any account. Please try again.")

               return redirect("enter_email_verification")   
     else: 
          form = EmailVerifcationForm()
     
     return render(request, "heaven_project_code/forgot_password/enter_email.html", {"form": form})

# Verifiying email 
def verify_email_password_reset(request, uidb64, token):
     try: 
          # decoding user id and getting user
          uid = urlsafe_base64_decode(uidb64).decode()
          user = User.objects.get(pk=uid)
     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
          user = None
     
     # Checking if user and token are valid and password form is used to change forgotten password
     if user and default_token_generator.check_token(user, token):

          if request.method == "POST":
               form = SetPasswordForm(user, request.POST)
               
               # Checking if form is valid
               if form.is_valid():
                    form.save()
                    
                    return redirect("login")
          else:
               form = SetPasswordForm(user)

          return render(request, "heaven_project_code/forgot_password/reset_password.html", {'form' : form})

     return HttpResponse("Invalid or expired verification link")

# Home View
def home(request):
     return render(request,  "heaven_project_code/home/home.html" )

# Chatbot View
def chatbot(request):
     return render(request,  "heaven_project_code/chatbot/chatbot.html" )

# Creating Chatbot variable
bot = RuleBasedChatbot(pairs)

#Function used to return responses from chatbot
def chatbot_response(request):
     user_message = request.GET.get("message", "")
     session  = request.session
     
     # Returning nearest services
     if "nearest shelter" in user_message or "Nearest Shelter" in user_message:
          session["intent"] = "find_shelter" 
          return JsonResponse({"response" : "Ok, please enter your postcode so i can find nearby shelters"})
     elif "nearest food bank" in user_message or "Nearest Food Bank" in user_message:
          session["intent"] = "find_foodbanks"
          return JsonResponse({"response" : "Ok, please enter your postcode so i can find nearby food banks"})
     elif "nearest support service" in user_message or "Nearest Support Service" in user_message:
          session["intent"] = "find_support_services"

     # Returning specific services
     elif "Specific Food Bank" in user_message or "specific food bank" in user_message:
          session["intent"] = "specific_foodbank"
          return JsonResponse({"response" : "Ok, please enter the name of the food bank."})
     elif "Specific Shelter" in user_message or "specific shelter" in user_message:
          session["intent"] = "specific_shelter"
          return JsonResponse({"response" : "Ok, please enter the name of the shelter."})
     elif "Specific Support Service" in user_message or "specific support service" in user_message:
          session["intent"] = "specific_support_service"
          return JsonResponse({"response" : "Ok, please enter the name of the support service."})
     
    
     # Finding nearest shelter
     if session.get("intent") == "find_shelter":
          postcode = user_message

          shelters = get_nearest_shelters(postcode)

          session["intent"] = None

          if not shelters:
               return JsonResponse({
                    "response": "Sorry, I couldn't find shelters near that postcode"
               })
          
          reply = "Here are the 5 nearest shelters:<br><br>"

          for s in shelters[:5]:
               reply += f"{s.name}<br>"
               reply += f"Postcode: {s.postcode}<br><br>"
     
          return JsonResponse({"response" : reply})
     
     # Finding nearest food banks
     elif session.get("intent") == "find_foodbanks":
          postcode = user_message

          food_banks = get_nearest_food_banks(postcode)

          session["intent"] = None

          if not food_banks:
               return JsonResponse({
                    "response": "Sorry, I couldn't find shelters near that postcode"
               })
          
          reply = "Here are the 5 nearest food banks:<br><br>"

          for fb in food_banks[:5]:
               reply += f"{fb.name}<br>"
               reply += f"Postcode: {fb.postcode}<br><br>"
     
          return JsonResponse({"response" : reply})
     
     # Finding nearest support services
     
     elif session.get("intent") == "find_support_services":
          postcode = user_message

          support_services = get_nearest_support_services(postcode)

          session["intent"] = None

          if not support_services:
               return JsonResponse({
                    "response": "Sorry, I couldn't find support services near that postcode"
               })
          
          reply = "Here are the 5 nearest support services:<br><br>"

          for ss in support_services[:5]:
               reply += f"{ss.name}<br>"
               reply += f"Postcode: {ss.postcode}<br><br>"
     
          return JsonResponse({"response" : reply})
     
     # Returns user back to home page
     elif "bye" in user_message or "exit" in user_message:
          session["intent"] = None
          return JsonResponse({
               "response": "Goodbye",
               "redirect": "home"
          })
     
     # Finding specific food bank
     elif session.get("intent") == "specific_foodbank":
          name_of_service = user_message

          food_bank = Food_Banks.objects.filter(name__icontains=name_of_service).first()
          
          session["intent"] = None

          if not food_bank:
               return JsonResponse({
                    "response": "Food Bank hasn't been found, please re-enter 'Specific Food Bank'"
               })
          
          reply = "Here is more information on the food bank.<br><br>"
          reply += f"Name: {food_bank.name}<br><br>"
          reply += f"City: {food_bank.city}<br><br>"
          reply += f"Country: {food_bank.country}<br><br>"
          reply += f"Address: {food_bank.address}<br><br>"
          reply += f"Postcode: {food_bank.postcode}<br><br>"
          reply += f"Type: {food_bank.type}<br><br>"
          reply += f"Phone: {food_bank.phone_number}<br><br>"

          return JsonResponse({"response" : reply})

     # Finding specific shelters
     elif session.get("intent") == "specific_shelter":
          name_of_service = user_message

          shelter = Shelters.objects.filter(name__icontains=name_of_service).first()
          
          session["intent"] = None

          if not shelter:
               return JsonResponse({
                    "response": "Shelter hasn't been found, please re-enter 'Specific Shelter'"
               })
          
          reply = "Here is more information on the shelter .<br><br>"
          reply += f"Name: {shelter.name}<br><br>"
          reply += f"City: {shelter.city}<br><br>"
          reply += f"Country: {shelter.country}<br><br>"
          reply += f"Address: {shelter.address}<br><br>"
          reply += f"Postcode: {shelter.postcode}<br><br>"
          reply += f"Type: {shelter.type}<br><br>"
          reply += f"Phone: {shelter.phone_number}<br><br>"

          
          return JsonResponse({"response" : reply})
     
     # Finding specific support service
     elif session.get("intent") == "specific_support_service":
          name_of_service = user_message

          support_service = Support_Services.objects.filter(name__icontains=name_of_service).first()
          
          session["intent"] = None

          if not support_service:
               return JsonResponse({
                    "response": "Support Service hasn't been found, please re-enter 'Specific Support Service'"
               })
          
          reply = "Here is more information on the support service.<br><br>"
          reply += f"Name: {support_service.name}<br><br>"
          reply += f"City: {support_service.city}<br><br>"
          reply += f"Country: {support_service.country}<br><br>"
          reply += f"Address: {support_service.address}<br><br>"
          reply += f"Postcode: {support_service.postcode}<br><br>"
          reply += f"Type: {support_service.type}<br><br>"
          reply += f"Phone: {support_service.phone_number}<br><br>"

          return JsonResponse({"response" : reply})
          

    # Chatbot responding to user's message
     response = bot.respond(user_message)
     return JsonResponse({"response" : response})

def services(request): 
     # Filtering Variables
     countries = Country.objects.all()
     selected_country = request.GET.get('country')
     selected_city = request.GET.get('city')
     postcode = request.GET.get('postcode')
     
     # Cities on in the country selected
     if selected_country:
          cities = City.objects.filter(country_id=selected_country)
     else:
          cities = City.objects.all()
     
     # Collecting all services
     food_banks = Food_Banks.objects.all()
     shelters = Shelters.objects.all()
     support_services = Support_Services.objects.all()

     query = request.GET.get('q', '')
     
     # Filter results based on user's queries
     if query:
          food_banks =  Food_Banks.objects.filter(
               Q(city__name__icontains=query) | Q(country__name__icontains=query) | Q(name__icontains=query))
          

          shelters = Shelters.objects.filter(
               Q(city__name__icontains=query) | Q(country__name__icontains=query) | Q(name__icontains=query))

          support_services = Support_Services.objects.filter(
               Q(city__name__icontains=query) | Q(country__name__icontains=query) | Q(name__icontains=query))
    
     # Filter results based on selected countries
     if selected_country:
          food_banks = food_banks.filter(country_id=selected_country)
          shelters = shelters.filter(country_id = selected_country)
          support_services = support_services.filter(country_id = selected_country)
     
     # Filter results based on selected cities
     if selected_city:
          food_banks = food_banks.filter(city_id = selected_city)
          shelters = shelters.filter(city_id = selected_city)
          support_services = support_services.filter(city_id = selected_city) 
     
     # User longitude and latitude
     user_lat = None
     user_lon = None

    
     user_latitude = request.GET.get('latitude')
     user_longitude = request.GET.get('longitude')

    # If user uses their own location
     if user_latitude and user_longitude:
          try:
               user_lat = float(user_latitude)
               user_lon = float(user_longitude)
          except ValueError:
               pass

     # If user uses postcode instead
     if (user_lat is None or user_lon is None) and postcode:
          user_lat, user_lon = get_point_from_postcode(postcode)
          
     
     def filter_by_distance(queryset):
          results = []
          # Collecting each service
          for item in queryset:
               # Checking for service longitude and latitude
               if item.latitude is not None and item.longitude is not None:
                    dist = distance_km(user_lat, user_lon, item.latitude, item.longitude)
                    
                    # Appened services less than 500 kilometers
                    if dist < 500:
                         item.distance = round(dist, 2)
                         results.append(item)
         
          # Sorting from shorest distance to longest
          return sorted(results, key=lambda x: x.distance)

     # Displaying services from shortest to furthest distance          
     if user_lat is not None and user_lon is not None:
          food_banks = filter_by_distance(food_banks)
          shelters = filter_by_distance(shelters)
          support_services = filter_by_distance(support_services)

     return render(request,  "heaven_project_code/services/services.html", {'countries' : countries, 'cities': cities, 'selected_country' : selected_country, 
     'selected_city' : selected_city, 'query' : query, 'food_banks': food_banks, 'shelters': shelters, 'support_services' : support_services} )

# Deleteing food bank review
class ReviewDeleteViewFoodBank(LoginRequiredMixin, DeleteView):
     model = Review_FoodBank
     template_name = "heaven_project_code/services/food_bank/delete_review_foodbank.html"
     success_url = '/'
     
     # Sending user back to the food bank detail
     def get_success_url(self):

          foodbank_id = self.object.foodbank_id.id
          
          return reverse('foodbank_details', kwargs={'id': foodbank_id})
     
     # Checks for the correct user deleting review
     def dispatch(self, request, *args, **kwargs):
         obj = self.get_object()
         
         if obj.user != request.user:
              raise PermissionDenied

         return super().dispatch(request, *args, **kwargs)


# Updating Food bank view
class ReviewUpdateViewFoodBank(LoginRequiredMixin, UpdateView):
     model = Review_FoodBank
     template_name = "heaven_project_code/services/food_bank/update_review_foodbank.html"
     
     # Parsing Form
     form_class = ReviewFoodBankForm

     # Return view
     def get_success_url(self):

          foodbank_id = self.object.foodbank_id.id
          
          return reverse('foodbank_details', kwargs={'id': foodbank_id})
     
     # Providng option
     def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs
     
     # Checking for the correct user
     def dispatch(self, request, *args, **kwargs):
         obj = self.get_object()
         
         if obj.user != request.user:
              raise PermissionDenied
         
        

         return super().dispatch(request, *args, **kwargs)
     


def foodbank_details(request, id):
     food_bank = get_object_or_404(Food_Banks, pk=id)
     
     # Getting reviews on the food bank
     reviews = Review_FoodBank.objects.filter(foodbank_id = food_bank)
     
     if request.method == "POST":
          
          form = ReviewFoodBankForm(request.POST, user=request.user)
          # Checks if form is valid
          if form.is_valid():
               # Attaching Food bank id before saving the form.
               review = form.save(commit=False)
               review.foodbank_id = food_bank
               review.user = request.user
               review.save()
     else:
          form = ReviewFoodBankForm(user=request.user)

     return render(request, 'heaven_project_code/services/food_bank/food_bank.html', {'food_bank': food_bank, 'form': form, 'reviews': reviews})

# Deleting Shelter Review
class ReviewDeleteViewShelter(LoginRequiredMixin, DeleteView):
     model = Review_Shelter
     template_name = "heaven_project_code/services/shelters/delete_review_shelter.html"
     success_url = '/'
     
     # Returing user back to shelter details
     def get_success_url(self):

          shelter_id = self.object.shelter_id.id
          
          return reverse('shelter_details', kwargs={'id': shelter_id})
     
     # Checking for correct user
     def dispatch(self, request, *args, **kwargs):
         obj = self.get_object()
         
         if obj.user != request.user:
              raise PermissionDenied

         return super().dispatch(request, *args, **kwargs)


# Update Shelter
class ReviewUpdateViewShelter(LoginRequiredMixin, UpdateView):
     model = Review_Shelter
     template_name = "heaven_project_code/services/shelters/update_review_shelter.html"
     
     form_class = ReviewShelterForm

     # Return view
     def get_success_url(self):

          shelter_id = self.object.shelter_id.id
          
          return reverse('shelter_details', kwargs={'id': shelter_id})
     
     # Option to choose username or annoymous
     def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

     # Checking for the correct user
     def dispatch(self, request, *args, **kwargs):
         obj = self.get_object()
         
         if obj.user != request.user:
              raise PermissionDenied
         
        

         return super().dispatch(request, *args, **kwargs)

# Shelter Details
def shelter_details(request, id):
     shelter = get_object_or_404(Shelters, pk=id)
     
     # Getting reviews for the shelter
     reviews = Review_Shelter.objects.filter(shelter_id = shelter)
     
     if request.method == "POST":
          
          form = ReviewShelterForm(request.POST, user=request.user)
          # Checking if form is valid
          if form.is_valid():
               # Attaching Shelter id before saving the form.
               review = form.save(commit=False)
               review.shelter_id = shelter
               review.user = request.user
               review.save()
     else:
          form = ReviewShelterForm(user=request.user)
      
     return render(request, 'heaven_project_code/services/shelters/shelters.html', {'shelter': shelter, 'form': form, 'reviews': reviews})


# Deleting Support Service Review
class ReviewDeleteViewSupportService(LoginRequiredMixin, DeleteView):
     model = Review_Support_Service
     template_name = "heaven_project_code/services/support_services/delete_review_support_services.html"
     success_url = '/'
     
     # Sending user back to the sheler details
     def get_success_url(self):

          support_service_id = self.object.support_service_id.id
          
          return reverse('support_service_details', kwargs={'id': support_service_id})


     # Checking for the correct user
     def dispatch(self, request, *args, **kwargs):
         obj = self.get_object()
         
         if obj.user != request.user:
              raise PermissionDenied

         return super().dispatch(request, *args, **kwargs)


# Update Shelter
class ReviewUpdateViewSupportService(LoginRequiredMixin, UpdateView):
     model = Review_Support_Service
     template_name = "heaven_project_code/services/support_services/update_review_support_services.html"
     
     # Providing form
     form_class = ReviewShelterForm

     # Return view
     def get_success_url(self):

          support_service_id = self.object.support_service_id.id
          
          return reverse('support_service_details', kwargs={'id': support_service_id})
     
     # Option between username or annoymous
     def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs
     
     # Checking for correct user
     def dispatch(self, request, *args, **kwargs):
         obj = self.get_object()
         
         if obj.user != request.user:
              raise PermissionDenied
         
        

         return super().dispatch(request, *args, **kwargs)

# Support Service Details
def support_service_details(request, id):
     support_service = get_object_or_404(Support_Services, pk=id)
     
     # Returning reviews on support service
     reviews = Review_Support_Service.objects.filter(support_service_id = support_service)
     
     if request.method == "POST":
          
          form = ReviewSupportServiceForm(request.POST, user=request.user)
          
          # Getting reviews on the Support Service
          if form.is_valid():
               # Attaching Support Service id before saving the form.
               review = form.save(commit=False)
               review.support_service_id = support_service
               review.user = request.user
               review.save()
     else:
          form = ReviewSupportServiceForm(user=request.user)
      
     return render(request, 'heaven_project_code/services/support_services/support_services.html', {'support_service': support_service, 'form': form, 'reviews': reviews})



@login_required
def edit_account(request):
     # Editing page with user's reviews
     review_food_bank = Review_FoodBank.objects.filter(user = request.user)
     review_support_service = Review_Support_Service.objects.filter(user = request.user)
     review_shelter = Review_Shelter.objects.filter(user = request.user)

     return render(request, 'heaven_project_code/edit_account/edit.html', {'review_food_bank' : review_food_bank, 'review_support_service' : review_support_service, 'review_shelter' : review_shelter})

@login_required
# Changing password
def change_password(request):
     if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        # Checks if form is valid
        if form.is_valid():
            form.save()
            
            #Sends user to login page
            return redirect("login")


     else:
          form = PasswordChangeForm(user=request.user, data=request.POST)

     return render(request, 'heaven_project_code/edit_account/change_password/change_password.html', {'form' : form})

@login_required
def update_profile(request):
     
     # Checks if profile has been created
     profile, created = Profile.objects.get_or_create(user=request.user)
     
     if request.method == "POST":
          profile_form = ProfilePictureForm(request.POST or None, request.FILES or None, instance=profile)
          
          # Checks if form is valid
          if profile_form.is_valid():
               profile_form.save()
     
     else:
          profile_form = ProfilePictureForm(instance=profile)

     return render(request, 'heaven_project_code/edit_account/update_profile/update_profile.html', {"profile_form" : profile_form, 'profile' : profile} )

@login_required
def update_email(request):
     if request.method =="POST":
          form = ChangeEmailForm(request.POST)
          # Checks if form is valid
          if form.is_valid():

               user = request.user
               
               # Collecting email from form
               email = form.cleaned_data["email"]
               
               # Temporaily holding user's email
               request.session["email"] = email
               
               # Creating verification link
               token = default_token_generator.make_token(user)
               uid = urlsafe_base64_encode(force_bytes(user.pk))
               current_site = get_current_site(request)
               verification_link = f"http://{current_site.domain}/change_email_verification/{uid}/{token}"
               
               # Sending email to the user
               send_mail( 
                    'Verify your email',
                    f'Click this link to verify your account: {verification_link}',
                    'noreply@havenproject.com',
                    [email],
                    fail_silently=False
               )

               return render(request, "heaven_project_code/edit_account/update_email/change_email_verification.html")
          
     else: 
          form = ChangeEmailForm()
     
     return render(request, "heaven_project_code/edit_account/update_email/update_email.html", {'form' : form})

@login_required
def change_email_verification(request, uidb64, token):
     try: 
          # Decoding user id form verification link
          uid = urlsafe_base64_decode(uidb64).decode()
          user = User.objects.get(pk=uid)
     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
          user = None
     
     # checking if user and token are valid
     if user and default_token_generator.check_token(user, token):
          
          # Getting email that was stored temporaily
          email = request.session.get("email")
         
          # Saves the user's email
          if email:
               user.email = email
               user.save()

          return render(request, 'heaven_project_code/edit_account/edit.html')
     else:
          return HttpResponse("Invalid or expired verification link")


# Google View for Sign In
@csrf_exempt
def sign_in(request):
    return render(request, 'heaven_project_code/login_register/login.html')
 
@csrf_exempt
def auth_receiver(request):
    """
    Google calls this URL after the user has signed in with their Google account.
    """
    print('Inside')
    token = request.POST['credential']

    # Requesting to get user's data  
    try:
        user_data = id_token.verify_oauth2_token(
            token, requests.Request(), os.environ['GOOGLE_OAUTH_CLIENT_ID']
        )
    except ValueError:
        return HttpResponse(status=403)
 
    # extracting data
    email = user_data["email"]
    
    # Checking if user exists
    user = User.objects.filter(email=email).first()
    
    #Logs in user or holds user's data temporaily to create an accounts
    if user:
         login(request, user)
         return redirect('home')
    else:
         request.session['temp_user'] = user_data
         return redirect("create_username")


def create_username(request):


     if request.method =="POST":
          form = EnterUsername(request.POST)
          
          # Getting user from google sso
          temp_user = request.session.get('temp_user')

          if not temp_user:
              return redirect('login')
          
          # Checking if form is valid
          if form.is_valid():
               username = form.cleaned_data['username']
              
               # Creates user object
               user = User.objects.create(
                    username=username,
                    email = temp_user['email']
               )

               # Stops holding user data temporaily
               del request.session['temp_user']
              
              # Logs in user
               login(request, user)

               return redirect('home')
          
     else:
          form = EnterUsername()


     return render(request, 'heaven_project_code/login_register/create_username.html', {"form" : form})
 
def sign_out(request):
    del request.session['user_data']
    return redirect('login')
     
     

