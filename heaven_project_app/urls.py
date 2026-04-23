from django.urls import path
from django.contrib.auth import views as auth_views
from .import views
from .views import ReviewDeleteViewFoodBank, ReviewUpdateViewFoodBank, ReviewDeleteViewShelter, ReviewUpdateViewShelter, ReviewDeleteViewSupportService, ReviewUpdateViewSupportService

urlpatterns = [
     path("", views.home, name="home"),
     path("login/", views.login_view, name="login"),
     path('sign-out', views.logout_view, name="sign_out"),
     path("delete-account/", views.delete_account, name="delete_account"),
     path("verify-email/<uidb64>/<token>/", views.verify_email, name="verify"),
     path('logout/', auth_views.LogoutView.as_view(), name='logout'),
     path("register/", views.register, name="register"),
     path("home/", views.home, name="home"),
     path("services/", views.services, name="services"),
     path("chatbot/", views.chatbot, name="chatbot"),

     path("food_banks/<int:id>", views.foodbank_details, name="foodbank_details"),
     path("food_banks/<int:pk>/delete/",  ReviewDeleteViewFoodBank.as_view(), name="delete_review_foodbank"),
     path("food_banks/<int:pk>/update/",  ReviewUpdateViewFoodBank.as_view(), name="update_review_foodbank"),

     path("shelters/<int:id>", views.shelter_details, name="shelter_details"),
     path("shelters/<int:pk>/delete/",  ReviewDeleteViewShelter.as_view(), name="delete_review_shelter"),
     path("shelters/<int:pk>/update/",  ReviewUpdateViewShelter.as_view(), name="update_review_shelter"),

     path("support_services/<int:id>", views.support_service_details, name="support_service_details"),
     path("support_services/<int:pk>/delete/",  ReviewDeleteViewSupportService.as_view(), name="delete_review_support_service"),
     path("support_services/<int:pk>/update/",  ReviewUpdateViewSupportService.as_view(), name="update_review_support_service"),

     path("enter_email", views.enter_email_verification, name="enter_email_verification"),
     path("verify_email_password_reset/<uidb64>/<token>/", views.verify_email_password_reset, name="verify"),
     path("edit_account/", views.edit_account, name="edit_account"),
     path("change_password/", views.change_password, name="change_password"),
     path("update_profile/", views.update_profile, name="update_profile"),
     path("update_email", views.update_email, name="update_email"),
     path("change_email_verification/<uidb64>/<token>/", views.change_email_verification, name="change_email_verrification"),
     path("create_username/", views.create_username, name="create_username"),
     path('auth-receiver', views.auth_receiver, name='auth-receiver'),  
     path('chatbot-response/', views.chatbot_response, name="chatbot_response")
]