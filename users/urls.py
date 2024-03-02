
from django.shortcuts import redirect
from django.urls import path, reverse_lazy

from users.views import RegistrationView, UserLoginView, logoutView, profileView, updateProfileView

urlpatterns = [
    path('login', UserLoginView.as_view(),  name='login'),
    path('logout', logoutView,  name='logout'),
    path('register', RegistrationView.as_view(), name='register'),
    path('profile', profileView, name='profile'),
    path('updateProfile', updateProfileView, name='updateProfile'),
]
