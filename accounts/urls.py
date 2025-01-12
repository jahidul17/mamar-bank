from django.urls import path,include
from .views import UserRegistrationView,UserLoginView,UserBankAccountUpdateView,ChangePasswordView
from .import views

urlpatterns = [
    path('register/',UserRegistrationView.as_view(),name='register'),
    path('login/',UserLoginView.as_view(),name='login'),
    path('logout/',views.user_logout,name='logout'),
    path('profile/',UserBankAccountUpdateView.as_view(),name='profile'),# profile page is not clear
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    
]
