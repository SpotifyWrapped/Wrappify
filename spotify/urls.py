from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('callback/', views.spotify_callback, name='spotify_callback'),
    path('profile/', views.get_user_profile, name='profile'),
    path('wraps/', views.wraps, name='wraps'),
    path('save_wrap/', views.save_wrap, name='save_wrap'),
    path('wraps_library/', views.wraps_library, name='wraps_library'),
    path('delete_wrap/<int:wrap_id>/', views.delete_wrap, name='delete_wrap'),
]
