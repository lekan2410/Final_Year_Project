from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db.models import Q
from .forms import RegisterForm
from .models import *
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import gettext as _

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
                    return redirect("home")
          
           
     else:
          form = AuthenticationForm()
     
     if request.user.is_authenticated:
          user_id = request.user.id
     
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

def verify_email(request, uidb64, token):
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
     

def home(request):
     if request.user.is_authenticated:
            user_id = request.user.id

     return render(request,  "heaven_project_code/home/home.html" )

def chatbot(request):
     return render(request,  "heaven_project_code/chatbot/chatbot.html" )

def services(request): 
     countries = Country.objects.all()
     cities = City.objects.none()
     selected_country = None
     selected_city = None

     food_banks = shelters = support_services = None

     query = request.GET.get('q', '')

     if query:
          food_banks =  Food_Banks.objects.filter(
               Q(city__name__icontains=query) | Q(country__name__icontains=query) | Q(name__icontains=query))
          

          shelters = Shelters.objects.filter(
               Q(city__name__icontains=query) | Q(country__name__icontains=query) | Q(name__icontains=query))

          support_services = Support_Services.objects.filter(
               Q(city__name__icontains=query) | Q(country__name__icontains=query) | Q(name__icontains=query))
    

     if request.method == 'POST':
          selected_country = request.POST.get('country')
          selected_city = request.POST.get('city')

          if selected_country:
               cities = City.objects.filter(country_id=selected_country)
     


     return render(request,  "heaven_project_code/services/services.html", {'countries' : countries, 'cities': cities, 'selected_country' : selected_country, 
     'selected_city' : selected_city, 'query' : query, 'food_banks': food_banks, 'shelters': shelters, 'support_services' : support_services} )






     
     

