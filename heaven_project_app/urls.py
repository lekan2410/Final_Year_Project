from django.urls import path
from django.contrib.auth import views as auth_views
from .import views

urlpatterns = [
     path("", views.home, name="home"),
     path("login/", views.login_view, name="login"),
     path("delete-account/", views.delete_account, name="delete_account"),
     path("verify-email/<uidb64>/<token>/", views.verify_email, name="verify"),
     path('logout/', auth_views.LogoutView.as_view(), name='logout'),
     path("register/", views.register, name="register"),
     path("home/", views.home, name="home"),
     path("services/", views.services, name="services"),
     path("chatbot/", views.chatbot, name="chatbot")
     
]