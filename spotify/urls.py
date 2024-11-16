from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('redirect/', views.spotifyLogin, name='redirect'),
    path('callback/', views.spotify_callback, name='spotify_callback'),
    path('profile/', views.profile, name='profile'),
    path('wraps/', views.wraps, name='wraps'),
    path('save_wrap/', views.save_wrap, name='save_wrap'),
    path('wraps_library/', views.wraps_library, name='wraps_library'),
    path('delete_wrap/<int:wrap_id>/', views.delete_wrap, name='delete_wrap'),
    path('wrap/<int:wrap_id>/', views.wrap_detail, name='wrap_detail'),
    path('contact/', views.contactPage, name='contacts'),
    path('settings/', views.settings, name='settings'),
    path('game/<int:wrap_id>/', views.game, name='game'),
    path('complete-game/<int:wrap_id>/', views.complete_game, name='complete_game'),


]