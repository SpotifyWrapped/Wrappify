from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('redirect/', views.loginPage, name='redirect'),
    path('callback/', views.spotify_callback, name='spotify_callback'),
    path('profile/', views.profile, name='profile'),
    path('wraps/', views.wraps, name='wraps'),
]