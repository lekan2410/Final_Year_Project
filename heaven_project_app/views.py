import os


from django.views.generic import DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse

from .utils import *
from .chatbot import RuleBasedChatbot
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

pairs = [
     [r"hi|hello|hey|yo", ["Hello! How can I help you today?",
                         "Hi there! How may I assist you?"]],
     [r"my name is (.*)", ["Hello %1! How can I assist you today?"]],
     [r"(.*) your name?", ["I am your friendly chatbot!"]],
     [r"how are you?", ["I'm just a bot, but I'm doing well. How about you?"]],
     [r"tell me a joke", ["Why don't skeletons fight each other? They don't have the guts!",
                         "Can a horse join the army, no the Neigh-vy",
                         "What did the cop say to his belly button?, You're under a vest!",]],
     [r"help|assist", ["Sure! here are the things I can do, <br><br> I can search for the nearest locations on shelters, "
     "food banks and support services<br><br>, I can tell you information on a specific service<br><br> send you links to specific pages on the website<br><br> use 'Commands' to find more information and remember i'm still in development."]],
     [r"bye|exit", ["Goodbye! Have a great day!", "See you later!"]],
     [r"i'm fine|i'm great|im great|im fine", ["That's great to hear!", "Wow that's wonderful to hear!"]],
     [r"How does this website help?", ["This website helps to allow people to find services to support those who are experincing homelessness"]],
     [r"What can you do?", ["I can answer questions, help you find services and tell jokes!"]],
     

     [r"where can i find nearest shelter?|where can i find shelters?| nearest shelters", ["SHOW_NEAREST_SHELTERS"]],
     [r"where can i find nearest food bank?|where can i find food banks?", ["SHOW_NEAREST_FOODBANKS."]],
     [r"where can i find nearest support service?|where can i find support services?", ["SHOW_NEAREST_SUPPORTS_SERVICES."]],

     [r"general information", ["This is a website that helps those who are experiencing homeless or people that are vulnerable to find services to support them. Food banks, Shelters and Support Services available. "]],

     [r"features|feature", ["Users can leave reviews on services, <br><br> - edit their profile and use me to find out more information, <br><br> - navigate the website or use me to tell jokes!"]],
     
     [r"(commands)", ["Here are some things you can type:<br><br>"
               "- 'Where can I find a shelter?'<br><br>"
               "- 'Find a food bank near me'<br><br>"
               "- 'Where can I find support services?'<br><br>"
               "- 'Tell me a joke'<br><br>"
               "- 'What can you do?'<br><br>"
               "- 'General information'<br><br>"
               "- 'Features'<br><br>"
               "- 'Help'<br><br>"
               "- 'Limitations on Location'<br><br>"
               "- 'Bye' or 'Exit' to leave the chat<br><br>"
               "You don’t have to type these exactly—I’ll try to understand similar questions too!"]],
     
     [r"Limitations on Location|limitation on location", ["Services available are only based on Cambridge due to early stages of development. <br><br> Use postcodes that are in Cambridge. <br><br> Using other postcodes outside of Cambridge may or may not return nearest results. <br><br> More Services will be available in the future."]],
     

     [r"(.*)", ["I'm sorry, I didn’t quite understand that.\n\n"
               "You can try things like:<br><br>"
               "- 'Where can I find a shelter?'<br><br>"
               "- 'Find a food bank'<br><br>"
               "- Type 'commands' to see all options"]],

     ]

# Create your views here.
def login_view(request):
     if request.method == "POST":
          form = AuthenticationForm(request, data=request.POST)

     
          if form.is_valid():
               user = form.get_user()
               
               if not user.is_active:
                    form.add_error(None, "Email not verified. Check your inbox" )
               else:
                    login(request, user) 
                    return redirect("/")
          
           
     else:
          form = AuthenticationForm()
     
     #if request.user.is_authenticated:
         # user_id = request.user.id
     
     return render(request, "heaven_project_code/login_register/login.html", {"form" : form} )

def logout_view(request): 
     logout(request)

     return render(request,  "heaven_project_code/home/home.html" )
     

def delete_account(request):
     if request.method == "POST":
          user = request.user
          logout(request)
          user.delete()
     
     return redirect("login")

def register(request):

     if request.user.is_authenticated:
          logout(request)
     
     if request.method =="POST":
          form = RegisterForm(request.POST)

          if form.is_valid():
               user = form.save()
               user.is_active = False
               user.save()

               token = default_token_generator.make_token(user)
               uid = urlsafe_base64_encode(force_bytes(user.pk))
               current_site = get_current_site(request)
               verification_link = f"http://{current_site.domain}/verify-email/{uid}/{token}"
               
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

# ChatGPT used to help create verification email.

def verify_email(uidb64, token):
     try:
          uid = urlsafe_base64_decode(uidb64).decode()
          user = User.objects.get(pk=uid)
     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
          user = None
     
     if user and default_token_generator.check_token(user, token):
          user.is_active = True
          user.save()
          return HttpResponse("Email verified! You can now log in" )
     else:
          return HttpResponse("Invalid or expired verification link")

def enter_email_verification(request):
     if request.method =="POST":
          form = EmailVerifcationForm(request.POST)
          

          if form.is_valid():

               try:
                    email = form.cleaned_data['email']

                    user = User.objects.get(email=email)
                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    current_site = get_current_site(request)
                    verification_link = f"http://{current_site.domain}/verify_email_password_reset/{uid}/{token}"
                    
                    send_mail(
                         'Verify your email',
                         f'Click this link to verify your account: {verification_link}',
                         'noreply@havenproject.com',
                         [user.email],
                         fail_silently=False
                    )
               except User.DoesNotExist:
                    pass

               return redirect("enter_email_verification")   
     else: 
          form = EmailVerifcationForm()
     
     return render(request, "heaven_project_code/forgot_password/enter_email.html", {"form": form})


def verify_email_password_reset(request, uidb64, token):
     try:
          uid = urlsafe_base64_decode(uidb64).decode()
          user = User.objects.get(pk=uid)
     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
          user = None
     
     if user and default_token_generator.check_token(user, token):

          if request.method == "POST":
               form = SetPasswordForm(user, request.POST)

               if form.is_valid():
                    form.save()
                    
                    return redirect("login")
          else:
               form = SetPasswordForm(user)

          return render(request, "heaven_project_code/forgot_password/reset_password.html", {'form' : form})

     return HttpResponse("Invalid or expired verification link")

def home(request):
     return render(request,  "heaven_project_code/home/home.html" )

def chatbot(request):
     return render(request,  "heaven_project_code/chatbot/chatbot.html" )


bot = RuleBasedChatbot(pairs)

def chatbot_response(request):
     user_message = request.GET.get("message", "")
     session  = request.session
     
     if "shelter" in user_message:
          session["intent"] = "find_shelter" 

          return JsonResponse({"response" : "Ok, please enter your postcode so i can find nearby shelters"})
     elif "food bank" in user_message:
          session["intent"] = "find_foodbanks"
          return JsonResponse({"response" : "Ok, please enter your postcode so i can find nearby food banks"})
     elif "support service" in user_message:
          session["intent"] = "find_support_services"
          
          return JsonResponse({"response" : "Ok, please enter your postcode so i can find nearby support services"})
     
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


     response = bot.respond(user_message)
     return JsonResponse({"response" : response})

def services(request): 
     countries = Country.objects.all()
     selected_country = request.GET.get('country')
     selected_city = request.GET.get('city')
     postcode = request.GET.get('postcode')
     

     if selected_country:
          cities = City.objects.filter(country_id=selected_country)
     else:
          cities = City.objects.all()

     food_banks = Food_Banks.objects.all()
     shelters = Shelters.objects.all()
     support_services = Support_Services.objects.all()

     query = request.GET.get('q', '')

     if query:
          food_banks =  Food_Banks.objects.filter(
               Q(city__name__icontains=query) | Q(country__name__icontains=query) | Q(name__icontains=query))
          

          shelters = Shelters.objects.filter(
               Q(city__name__icontains=query) | Q(country__name__icontains=query) | Q(name__icontains=query))

          support_services = Support_Services.objects.filter(
               Q(city__name__icontains=query) | Q(country__name__icontains=query) | Q(name__icontains=query))
    

     if selected_country:
          food_banks = food_banks.filter(country_id=selected_country)
          shelters = shelters.filter(country_id = selected_country)
          support_services = support_services.filter(country_id = selected_country)
     
     if selected_city:
          food_banks = food_banks.filter(city_id = selected_city)
          shelters = shelters.filter(city_id = selected_city)
          support_services = support_services.filter(city_id = selected_city) 
     
     user_lat = None
     user_lon = None

    
     user_latitude = request.GET.get('latitude')
     user_longitude = request.GET.get('longitude')

   
     if user_latitude and user_longitude:
          try:
               user_lat = float(user_latitude)
               user_lon = float(user_longitude)
          except ValueError:
               pass


     if (user_lat is None or user_lon is None) and postcode:
          user_lat, user_lon = get_point_from_postcode(postcode)
          
     
     def filter_by_distance(queryset):
          results = []
          for item in queryset:
               
               if item.latitude is not None and item.longitude is not None:
                    dist = distance_km(user_lat, user_lon, item.latitude, item.longitude)

                    if dist < 500:
                         item.distance = round(dist, 2)
                         results.append(item)

          return sorted(results, key=lambda x: x.distance)
               
     if user_lat is not None and user_lon is not None:
          food_banks = filter_by_distance(food_banks)
          shelters = filter_by_distance(shelters)
          support_services = filter_by_distance(support_services)

     return render(request,  "heaven_project_code/services/services.html", {'countries' : countries, 'cities': cities, 'selected_country' : selected_country, 
     'selected_city' : selected_city, 'query' : query, 'food_banks': food_banks, 'shelters': shelters, 'support_services' : support_services} )


class ReviewDeleteViewFoodBank(LoginRequiredMixin, DeleteView):
     model = Review_FoodBank
     template_name = "heaven_project_code/services/food_bank/delete_review_foodbank.html"
     success_url = '/'

     def get_success_url(self):

          foodbank_id = self.object.foodbank_id.id
          
          return reverse('foodbank_details', kwargs={'id': foodbank_id})

     def dispatch(self, request, *args, **kwargs):
         obj = self.get_object()
         
         if obj.user != request.user:
              raise PermissionDenied

         return super().dispatch(request, *args, **kwargs)

# ChatGPT and GeeksforGeeks used for guidance and then modified the solution to fit my own implementation 
class ReviewUpdateViewFoodBank(LoginRequiredMixin, UpdateView):
     model = Review_FoodBank
     template_name = "heaven_project_code/services/food_bank/update_review_foodbank.html"
     
     form_class = ReviewFoodBankForm

     # Return view
     def get_success_url(self):

          foodbank_id = self.object.foodbank_id.id
          
          return reverse('foodbank_details', kwargs={'id': foodbank_id})
     

     def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

     def dispatch(self, request, *args, **kwargs):
         obj = self.get_object()
         
         if obj.user != request.user:
              raise PermissionDenied
         
        

         return super().dispatch(request, *args, **kwargs)
     


def foodbank_details(request, id):
     food_bank = get_object_or_404(Food_Banks, pk=id)
     
     reviews = Review_FoodBank.objects.filter(foodbank_id = food_bank)
     
     if request.method == "POST":
          
          form = ReviewFoodBankForm(request.POST, user=request.user)

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

     def get_success_url(self):

          shelter_id = self.object.shelter_id.id
          
          return reverse('shelter_details', kwargs={'id': shelter_id})

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
     

     def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

     def dispatch(self, request, *args, **kwargs):
         obj = self.get_object()
         
         if obj.user != request.user:
              raise PermissionDenied
         
        

         return super().dispatch(request, *args, **kwargs)

def shelter_details(request, id):
     shelter = get_object_or_404(Shelters, pk=id)
     
     reviews = Review_Shelter.objects.filter(shelter_id = shelter)
     
     if request.method == "POST":
          
          form = ReviewShelterForm(request.POST, user=request.user)

          if form.is_valid():
               # Attaching Shelter id before saving the form.
               review = form.save(commit=False)
               review.shelter_id = shelter
               review.user = request.user
               review.save()
     else:
          form = ReviewShelterForm(user=request.user)
      
     return render(request, 'heaven_project_code/services/shelters/shelters.html', {'shelter': shelter, 'form': form, 'reviews': reviews})


# Deleting Shelter Review
class ReviewDeleteViewSupportService(LoginRequiredMixin, DeleteView):
     model = Review_Support_Service
     template_name = "heaven_project_code/services/support_services/delete_review_support_services.html"
     success_url = '/'

     def get_success_url(self):

          support_service_id = self.object.support_service_id.id
          
          return reverse('support_service_details', kwargs={'id': support_service_id})

     def dispatch(self, request, *args, **kwargs):
         obj = self.get_object()
         
         if obj.user != request.user:
              raise PermissionDenied

         return super().dispatch(request, *args, **kwargs)


# Update Shelter
class ReviewUpdateViewSupportService(LoginRequiredMixin, UpdateView):
     model = Review_Support_Service
     template_name = "heaven_project_code/services/support_services/update_review_support_services.html"
     
     form_class = ReviewShelterForm

     # Return view
     def get_success_url(self):

          support_service_id = self.object.support_service_id.id
          
          return reverse('support_service_details', kwargs={'id': support_service_id})
     

     def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

     def dispatch(self, request, *args, **kwargs):
         obj = self.get_object()
         
         if obj.user != request.user:
              raise PermissionDenied
         
        

         return super().dispatch(request, *args, **kwargs)

def support_service_details(request, id):
     support_service = get_object_or_404(Support_Services, pk=id)
     
     reviews = Review_Support_Service.objects.filter(support_service_id = support_service)
     
     if request.method == "POST":
          
          form = ReviewSupportServiceForm(request.POST, user=request.user)

          if form.is_valid():
               # Attaching Shelter id before saving the form.
               review = form.save(commit=False)
               review.support_service_id = support_service
               review.user = request.user
               review.save()
     else:
          form = ReviewSupportServiceForm(user=request.user)
      
     return render(request, 'heaven_project_code/services/support_services/support_services.html', {'support_service': support_service, 'form': form, 'reviews': reviews})

def testing(request):

     return render(request, 'heaven_project_code/test/testing.html')

def edit_account(request):
     return render(request, 'heaven_project_code/edit_account/edit.html')

def change_password(request):
     if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
     else:
          form = PasswordChangeForm(user=request.user, data=request.POST)

     return render(request, 'heaven_project_code/edit_account/change_password/change_password.html', {'form' : form})

def update_profile(request):
     
     # Checks if profile has been created
     profile, created = Profile.objects.get_or_create(user=request.user)
     
     if request.method == "POST":
          profile_form = ProfilePictureForm(request.POST or None, request.FILES or None, instance=profile)
          
          if profile_form.is_valid():
               profile_form.save()
     
     else:
          profile_form = ProfilePictureForm(instance=profile)

     return render(request, 'heaven_project_code/edit_account/update_profile/update_profile.html', {"profile_form" : profile_form, 'profile' : profile} )

def update_email(request):
     if request.method =="POST":
          form = ChangeEmailForm(request.POST)

          if form.is_valid():

               user = request.user
                
               email = form.cleaned_data["email"]

               request.session["email"] = email

               token = default_token_generator.make_token(user)
               uid = urlsafe_base64_encode(force_bytes(user.pk))
               current_site = get_current_site(request)
               verification_link = f"http://{current_site.domain}/change_email_verification/{uid}/{token}"
               
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

def change_email_verification(request, uidb64, token):
     try:
          uid = urlsafe_base64_decode(uidb64).decode()
          user = User.objects.get(pk=uid)
     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
          user = None
     
     if user and default_token_generator.check_token(user, token):
          
          email = request.session.get("email")

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
 
    try:
        user_data = id_token.verify_oauth2_token(
            token, requests.Request(), os.environ['GOOGLE_OAUTH_CLIENT_ID']
        )
    except ValueError:
        return HttpResponse(status=403)
 
    # In a real app, I'd also save any new user here to the database.
    # You could also authenticate the user here using the details from Google (https://docs.djangoproject.com/en/4.2/topics/auth/default/#how-to-log-a-user-in)
    email = user_data["email"]

    user = User.objects.filter(email=email).first()

    if user:
         login(request, user)
         return redirect('home')
    else:
         request.session['temp_user'] = user_data
         return redirect("create_username")


def create_username(request):


     if request.method =="POST":
          form = EnterUsername(request.POST)

          temp_user = request.session.get('temp_user')

          if not temp_user:
              return redirect('login')
          

          if form.is_valid():
               username = form.cleaned_data['username']

               user = User.objects.create(
                    username=username,
                    email = temp_user['email']
               )


               del request.session['temp_user']

               login(request, user)

               return redirect('home')
          
     else:
          form = EnterUsername()


     return render(request, 'heaven_project_code/login_register/create_username.html', {"form" : form})
 
def sign_out(request):
    del request.session['user_data']
    return redirect('login')
     
     

