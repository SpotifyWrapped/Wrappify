from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.homePage, name='home'),
    path('redirect/', views.spotifyLogin, name='redirect'),
    path('callback/', views.spotify_callback, name='spotify_callback'),
    path('profile/', views.profile, name='profile'),
]