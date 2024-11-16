import os
import time
import json
import requests
from collections import Counter
from urllib.parse import urlencode, quote
from django.conf import settings
from django.urls import reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.serializers.json import DjangoJSONEncoder

from .models import SavedWrap

# Get the custom user model
User = get_user_model()

# ========== Spotify App Credentials ==========

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SCOPE = "user-read-private user-read-email user-top-read"

# ========== Authentication Views ==========

# Render the login page
def loginPage(request):
    request.session.clear()
    return render(request, 'spotify/login.html')

# Log out from both Spotify and Django sessions
def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('login')

# Redirect the user to Spotify login page
def spotifyLogin(request):
    logout_url = "https://accounts.spotify.com/en/logout"
    auth_params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": SCOPE,
        "show_dialog": "true"
    }
    auth_url = f"{SPOTIFY_AUTH_URL}?{urlencode(auth_params)}"
    final_url = f"{logout_url}?continue={quote(auth_url)}"
    return redirect(final_url)

# Handle Spotify callback after user authorization
def spotify_callback(request):
    code = request.GET.get('code')
    if not code:
        return render(request, 'spotify/error.html', {"message": "Authorization failed."})

    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET,
    }

    try:
        token_response = requests.post(SPOTIFY_TOKEN_URL, data=token_data)
        token_response.raise_for_status()
        token_json = token_response.json()
    except requests.JSONDecodeError:
        print("Token response is not JSON:", token_response.text)
        return render(request, 'spotify/error.html', {"message": "Invalid response from Spotify. Please try again."})

    access_token = token_json.get('access_token')
    refresh_token = token_json.get('refresh_token')
    expires_in = token_json.get('expires_in')

    if access_token and refresh_token:
        request.session['access_token'] = access_token
        request.session['refresh_token'] = refresh_token
        request.session['token_expires_at'] = time.time() + expires_in

        # Call get_valid_token to verify the token's usability immediately after obtaining it
        if not get_valid_token(request):  # This is the new check
            return render(request, 'spotify/error.html', {
                "message": "Token validation failed. Please try logging in again."
            })

        headers = {'Authorization': f'Bearer {access_token}'}
        user_profile_response = requests.get('https://api.spotify.com/v1/me', headers=headers)

        if user_profile_response.status_code == 200:
            user_data = user_profile_response.json()
            email = user_data.get('email')
            display_name = user_data.get('display_name')

            try:
                user, created = User.objects.get_or_create(
                    username=email,
                    defaults={'email': email, 'first_name': display_name or ""}
                )
            except Exception as e:
                print(f"Error creating/retrieving user: {e}")
                return render(request, 'spotify/error.html', {"message": "Failed to create or retrieve user account. Please try again."})

            login(request, user)
            return redirect('profile')
        else:
            return render(request, 'spotify/error.html', {"message": "Failed to retrieve user profile from Spotify."})
    else:
        print("Token exchange response:", token_json)
        return render(request, 'spotify/error.html', {"message": "Token exchange failed. Please try again."})

# ========== Profile and Wrap Views ==========

# Display the user's profile with Spotify data
@login_required
def profile(request):
    time_range = request.GET.get('time_range')
    user_data = spotify_api_request(request, 'https://api.spotify.com/v1/me')

    if not user_data:
        return render(request, 'spotify/error.html', {'message': "Error fetching user data from Spotify API."})

    profile_image_url = user_data.get('images', [{}])[0].get('url') if user_data.get('images') else None
    
    context = {
        'user_data': user_data,
        'selected_time_range': time_range,
        'profile_image_url': profile_image_url  # Pass the profile image URL to the template
    }
    return render(request, 'spotify/profile.html', context)

# Display Spotify wrapped data
@login_required
def wraps(request):
    time_range = request.GET.get('time_range', None) or 'short_term'  # Default to 'short_term' if no parameter

    headers = {'Authorization': f'Bearer {get_valid_token(request)}'}
    user_data = spotify_api_request(request, 'https://api.spotify.com/v1/me')

    if not user_data:
        return render(request, 'spotify/error.html', {'message': "Error fetching user data from Spotify API."})

    # Define human-readable labels for each time range
    time_range_labels = {
        'short_term': 'Last Month',
        'medium_term': 'Last 6 Months',
        'long_term': 'All Time'
    }
    time_range_label = time_range_labels.get(time_range, 'Last Month')

    # Fetch user's top artists based on the selected time range
    artists_response = requests.get(f'https://api.spotify.com/v1/me/top/artists?limit=10&time_range={time_range}', headers=headers)
    all_artists = artists_response.json().get('items', []) if artists_response.status_code == 200 else []

    # Fetch user's top tracks based on the selected time range
    tracks_response = requests.get(f'https://api.spotify.com/v1/me/top/tracks?limit=10&time_range={time_range}', headers=headers)
    all_tracks = tracks_response.json().get('items', []) if tracks_response.status_code == 200 else []

    top_artist = all_artists[0] if all_artists else None
    top_5_artists = all_artists[:5]
    genres = [genre for artist in all_artists for genre in artist.get('genres', [])]
    top_genres = Counter(genres).most_common(5)
    top_5_tracks = all_tracks[:5]

    track_ids = [track['id'] for track in all_tracks]
    avg_danceability = avg_energy = avg_valence = None

    if track_ids:
        audio_features_json = spotify_api_request(request, 'https://api.spotify.com/v1/audio-features', params={'ids': ','.join(track_ids)})
        valid_features = [f for f in audio_features_json.get('audio_features', []) if f]
        if valid_features:
            avg_danceability = sum(f['danceability'] for f in valid_features) / len(valid_features)
            avg_energy = sum(f['energy'] for f in valid_features) / len(valid_features)
            avg_valence = sum(f['valence'] for f in valid_features) / len(valid_features)

    recommend_params = {
        'seed_artists': ','.join([artist['id'] for artist in all_artists[:2]]) if all_artists else '',
        'seed_tracks': ','.join([track['id'] for track in all_tracks[:2]]) if all_tracks else '',
        'limit': 5
    }
    recommendations_json = spotify_api_request(request, 'https://api.spotify.com/v1/recommendations', params=recommend_params)

    # wrap_data is the JSON object we will pass to the template
    wrap_data = {
        "title": "My Spotify Wrapped",
        "time_range_label": time_range_label,
        "top_genres": top_genres,
        "top_tracks": top_5_tracks,
        "avg_danceability": avg_danceability,
        "avg_energy": avg_energy,
        "avg_valence": avg_valence,
        "top_artist": top_artist,
        "top_artists": top_5_artists,
        "recommendations": recommendations_json.get('tracks', []) if recommendations_json else []
    }
    wrap_data_json = json.dumps(wrap_data, cls=DjangoJSONEncoder)

    return render(request, 'spotify/wraps.html', {
        'user_data': user_data,
        'wrap_data_json': wrap_data_json,
        'top_artist': top_artist,
        'artists': top_5_artists,
        'tracks': top_5_tracks,
        'recommendations': recommendations_json.get('tracks', []) if recommendations_json else [],
        'top_genres': top_genres,
        'avg_danceability': avg_danceability,
        'avg_energy': avg_energy,
        'avg_valence': avg_valence,
        'selected_time_range': time_range,
        'time_range_label': time_range_label
    })

# Display a list of saved wraps for the user
@login_required
def wraps_library(request):
    saved_wraps = SavedWrap.objects.filter(user=request.user)
    for wrap in saved_wraps:
        print(wrap.top_tracks)
    return render(request, 'spotify/wraps_library.html', {'saved_wraps': saved_wraps})

# Save the current Spotify wrap data to the database
@login_required
def save_wrap(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            wrap_data = {
                'user': request.user,
                'title': data.get('title', 'My Spotify Wrapped'),
                'time_range_label': data.get('time_range_label'),
                'total_playback_minutes': '0',
                'top_genres': data.get('top_genres'),
                'top_tracks': data.get('top_tracks'),
                'avg_danceability': float(data.get('avg_danceability', 0)),
                'avg_energy': float(data.get('avg_energy', 0)),
                'avg_valence': float(data.get('avg_valence', 0)),
                'top_artist': data.get('top_artist') or "No top artist available",  # Set default value
                'top_artists': data.get('top_artists'),
                'recommendations': data.get('recommendations')
            }
            SavedWrap.objects.create(**wrap_data)
            return JsonResponse({'message': 'Wrap saved successfully'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            print(f"Error saving wrap: {e}")
            return JsonResponse({'error': 'Failed to save wrap data'}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

# Delete a specific saved wrap
@login_required
@require_POST
def delete_wrap(request, wrap_id):
    wrap = get_object_or_404(SavedWrap, id=wrap_id, user=request.user)
    wrap.delete()
    return JsonResponse({'message': 'Wrap deleted successfully'})

# Saved Wrap details
def wrap_detail(request, wrap_id):
    # Get the wrap details or return a 404 if not found
    wrap = get_object_or_404(SavedWrap, id=wrap_id, user=request.user)
    
    # Prepare the context for the template
    context = {
        'title': wrap.title,
        'time_range_label': wrap.time_range_label,
        'top_genres': wrap.top_genres,
        'top_tracks': wrap.top_tracks,
        'avg_danceability': wrap.avg_danceability,
        'avg_energy': wrap.avg_energy,
        'avg_valence': wrap.avg_valence,
        'top_artist': wrap.top_artist,
        'artists': wrap.top_artists,
        'recommendations': wrap.recommendations,
        'created_at': wrap.created_at,
    }
    return render(request, 'spotify/saved_wraps.html', context)

# Settings Page
@login_required
def settings(request):
    return render(request, 'spotify/settings.html')

@login_required
def game(request, wrap_id):
    wrap = get_object_or_404(SavedWrap, id=wrap_id, user=request.user)
    wrap_data = {
        "title": wrap.title,
        "time_range_label": wrap.time_range_label,
        "top_genres": wrap.top_genres,
        "top_tracks": wrap.top_tracks,
        "top_artist": wrap.top_artist,
        'avg_danceability': wrap.avg_danceability,
        'avg_energy': wrap.avg_energy,
        'avg_valence': wrap.avg_valence,
        'recommendations': wrap.recommendations,
    }
    wrap_data_json = json.dumps(wrap_data, cls=DjangoJSONEncoder)
    
    return render(request, 'spotify/game.html', {
        'wrap_data_json': wrap_data_json,
        'wrap_id': wrap_id  # Pass wrap_id to template
    })

from django.shortcuts import redirect

@login_required
def complete_game(request, wrap_id):
    # Fetch the specific wrap for the logged-in user
    wrap = get_object_or_404(SavedWrap, id=wrap_id, user=request.user)
    wrap.completed_game = True  # Mark the game as completed
    wrap.save()  # Save changes to the database

    return JsonResponse({'message': 'Game marked as completed.'}, status=200)

# ========== Helper Functions ==========

# Retrieve a valid access token, refreshing if necessary
def get_valid_token(request):
    access_token = request.session.get('access_token')
    token_expires_at = request.session.get('token_expires_at')
    if access_token and time.time() < token_expires_at:
        return access_token

    refresh_success = refresh_token(request)
    if refresh_success:
        return request.session.get('access_token')
    else:
        return None

# Helper function: refreshes the access token

    return refresh_token(request)

# Refresh the Spotify access token using the refresh token
def refresh_token(request):
    refresh_token = request.session.get('refresh_token')
    if not refresh_token:
        return False

    refresh_data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET,
    }

    response = requests.post(SPOTIFY_TOKEN_URL, data=refresh_data)
    response_json = response.json()

    if 'access_token' in response_json:
        request.session['access_token'] = response_json['access_token']
        request.session['token_expires_at'] = time.time() + response_json.get('expires_in', 3600)
        return True
    else:
        print("Token refresh failed:", response_json)
        return False

# Make a request to the Spotify API with valid access token
def spotify_api_request(request, url, params=None):
    access_token = get_valid_token(request)
    if not access_token:
        return None
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Spotify API Request failed: {e}")
        return None

def contactPage(request):
    return render(request, 'spotify/contact.html')