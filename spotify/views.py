import os
import requests
import time
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from collections import Counter
from urllib.parse import urlencode, quote
from django.urls import reverse
from django.http import JsonResponse
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model

User = get_user_model()
# Spotify app credentials
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SCOPE = "user-read-private user-read-email user-top-read"

# Initial Welcome Page
def loginPage(request):
    return render(request, 'spotify/login.html')

#Logout from Spotify and Django session
def logout_view(request):
    logout(request)
    request.session.clear()
    return redirect('login')

# Login page will redirect to Spotify login
def spotifyLogin(request):
    logout_url = "https://accounts.spotify.com/en/logout"
    auth_params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,  # Ensure this is the exact URI registered in Spotify
        "scope": SCOPE,
        "show_dialog": "true"
    }
    auth_url = f"{SPOTIFY_AUTH_URL}?{urlencode(auth_params)}"
    final_url = f"{logout_url}?continue={quote(auth_url)}"

    return redirect(final_url)
     
# Spotify redirects back to this URL after user authorization
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
        return render(request, 'spotify/error.html', {
            "message": "Invalid response from Spotify. Please try again."
        })

    access_token = token_json.get('access_token')
    refresh_token = token_json.get('refresh_token')
    expires_in = token_json.get('expires_in')

    if access_token and refresh_token:
        request.session['access_token'] = access_token
        request.session['refresh_token'] = refresh_token
        request.session['token_expires_at'] = time.time() + expires_in

        # Call get_valid_token to verify the token's usability immediately after obtaining it
        if not get_valid_token(request):
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

# Display the user's profile
def profile(request):
    time_range = request.GET.get('time_range', 'short_term')
    user_data = spotify_api_request(request, 'https://api.spotify.com/v1/me')

    if not user_data:
        return render(request, 'spotify/error.html', {'message': "Error fetching user data from Spotify API."})

    context = {
        'user_data': user_data,
        'selected_time_range': time_range,  # Pass to highlight button
    }
    return render(request, 'spotify/profile.html', context)

# Display Wraps
def wraps(request):
    time_range = request.GET.get('time_range', 'short_term')
    headers = {'Authorization': f'Bearer {get_valid_token(request)}'}

    user_data = spotify_api_request(request, 'https://api.spotify.com/v1/me')
    if not user_data:
        return render(request, 'spotify/error.html', {'message': "Error fetching user data from Spotify API."})
    
    # Define human-readable labels for each time range
    time_range_labels = {
        'short_term': 'Last 4 Weeks',
        'medium_term': 'Last 6 Months',
        'long_term': 'All Time'
    }
    time_range_label = time_range_labels.get(time_range, 'Last Month')

    # Fetch user's top artists based on the selected time range
    artists_response = requests.get(
        f'https://api.spotify.com/v1/me/top/artists?limit=10&time_range={time_range}', headers=headers
    )
    if artists_response.status_code == 200:
        all_artists = artists_response.json().get('items', [])
    else:
        return render(request, 'spotify/error.html', {'message': "Error fetching artists data from Spotify API."})

    # Fetch user's top tracks based on the selected time range
    tracks_response = requests.get(
        f'https://api.spotify.com/v1/me/top/tracks?limit=10&time_range={time_range}', headers=headers
    )
    if tracks_response.status_code == 200:
        all_tracks = tracks_response.json().get('items', [])
    else:
        return render(request, 'spotify/error.html', {'message': "Error fetching tracks data from Spotify API."})

    top_artist = all_artists[0] if all_artists else None
    top_5_artists = all_artists[:5]

    genres = [genre for artist in all_artists for genre in artist.get('genres', [])]
    top_genres = Counter(genres).most_common(5)

    top_5_tracks = all_tracks[:5]
    total_playback_minutes = sum(track['duration_ms'] for track in all_tracks) / 60000

    track_ids = [track['id'] for track in all_tracks]
    avg_danceability = avg_energy = avg_valence = None

    # Fetch audio features for the tracks if there are track IDs
    if track_ids:
        audio_features_json = spotify_api_request(request, 'https://api.spotify.com/v1/audio-features', params={'ids': ','.join(track_ids)})
        if audio_features_json:
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

    return render(request, 'spotify/wraps.html', {
        'user_data': user_data,
        'top_artist': top_artist,
        'artists': top_5_artists,
        'tracks': top_5_tracks,
        'recommendations': recommendations_json.get('tracks', []) if recommendations_json else [],
        'total_playback_minutes': total_playback_minutes,
        'top_genres': top_genres,
        'avg_danceability': avg_danceability,
        'avg_energy': avg_energy,
        'avg_valence': avg_valence,
        'selected_time_range': time_range,
        'time_range_label': time_range_label  # Pass label for display in template
    })


# Helper function: retries the access token if it's expired
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

# Helper function: makes a request to the Spotify API (v1/me/top/artists, etc.)
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