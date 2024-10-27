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

def logout_view(request):
    # Log out from Django session
    logout(request)
    request.session.clear()
    return redirect('login')

# Login page will redirect to Spotify login
def spotifyLogin(request):
    # Step 2: Redirect to Spotify's logout URL with a redirect back to the authorization URL
    logout_url = "https://accounts.spotify.com/en/logout"

    # Prepare the Spotify authorization URL with all parameters including encoded redirect_uri
    auth_params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,  # Ensure this is the exact URI registered in Spotify
        "scope": SCOPE,
        "show_dialog": "true"
    }
    auth_url = f"{SPOTIFY_AUTH_URL}?{urlencode(auth_params)}"

    # Construct the final logout URL with a redirect to the encoded authorization URL
    final_url = f"{logout_url}?continue={quote(auth_url)}"

    # Redirect the user to Spotify logout followed by the authorization page
    return redirect(final_url)
     
def spotify_callback(request):
    code = request.GET.get('code')

    if not code:
        return render(request, 'spotify/error.html', {"message": "Authorization failed."})

    # Exchange the authorization code for tokens
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET,
    }

    token_response = requests.post(SPOTIFY_TOKEN_URL, data=token_data)

    try:
        token_json = token_response.json()
    except requests.JSONDecodeError:
        print("Token response is not JSON:", token_response.text)
        return render(request, 'spotify/error.html', {
            "message": "Invalid response from Spotify. Please try again."
        })

    if 'access_token' in token_json:
        access_token = token_json['access_token']
        refresh_token = token_json.get('refresh_token')
        expires_in = token_json['expires_in']  # Token lifetime in seconds

        # Save tokens and expiration time in session
        request.session['access_token'] = access_token
        request.session['refresh_token'] = refresh_token
        request.session['token_expires_at'] = time.time() + expires_in  # Expiration time

        headers = {
            'Authorization': f'Bearer {access_token}',
        }

        user_profile_response = requests.get('https://api.spotify.com/v1/me', headers=headers)
        if user_profile_response.status_code == 200:
            user_data = user_profile_response.json()
            email = user_data.get('email')
            display_name = user_data.get('display_name')

            # Create or retrieve the user in Django's database
            try:
                user, created = User.objects.get_or_create(
                    username=email,
                    defaults={
                        'email': email,
                        'first_name': display_name or "",  # Ensure display name is set, fallback to empty
                    }
                )
                print(f"User {'created' if created else 'retrieved'} successfully: {email}")
            except Exception as e:
                print(f"Error creating/retrieving user: {e}")
                return render(request, 'spotify/error.html', {"message": "Failed to create or retrieve user account. Please try again."})

            # Log in the user into the Django session
            login(request, user)
            # Redirect to the profile page after successful login
            return redirect('profile')

        else:
            return render(request, 'spotify/error.html', {"message": "Failed to retrieve user profile from Spotify."})
    else:
        # Log the response for debugging
        print("Token exchange response:", token_json)
        return render(request, 'spotify/error.html', {"message": "Token exchange failed."})

# Step 3: Display the user's profile
def profile(request):
    access_token = request.session.get('access_token')
    token_expires_at = request.session.get('token_expires_at')

    # Check if the access token exists and is still valid
    if not access_token or time.time() > token_expires_at:
        refresh_token(request)

    headers = {
        'Authorization': f'Bearer {request.session.get("access_token")}',
    }

    try:
        # Fetch user profile information
        user_profile_response = requests.get('https://api.spotify.com/v1/me', headers=headers)
        user_profile_response.raise_for_status()
        user_data = user_profile_response.json()

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return render(request, 'spotify/error.html', {'message': "Error fetching user data from Spotify API."})

    # Render the profile page with user info only
    return render(request, 'spotify/profile.html', {
        'user_data': user_data,
    })

# Step 4: Display Wraps
def wraps(request):
    access_token = request.session.get('access_token')
    token_expires_at = request.session.get('token_expires_at')

    # Check if the access token exists and is still valid
    if not access_token or time.time() > token_expires_at:
        refresh_token(request)

    headers = {
        'Authorization': f'Bearer {request.session.get("access_token")}',
    }

    try:
        # Fetch user profile information
        user_profile_response = requests.get('https://api.spotify.com/v1/me', headers=headers)
        user_profile_response.raise_for_status()
        user_data = user_profile_response.json()

        # Fetch the user's top artists (short-term data for the last 4 weeks)
        artists_response = requests.get('https://api.spotify.com/v1/me/top/artists?limit=10&time_range=short_term', headers=headers)
        artists_response.raise_for_status()
        artists_json = artists_response.json()
        all_artists = artists_json.get('items', [])

        # Fetch the number 1 artist (top artist)
        top_artist = all_artists[0] if all_artists else None

        # Display only the top 5 artists
        top_5_artists = all_artists[:5]

        # Extract and count genres from top artists
        genres = []
        for artist in all_artists:
            genres.extend(artist.get('genres', []))  # Add the artist's genres to the list

        # Use Counter to count occurrences of each genre
        genre_counts = Counter(genres)
        top_genres = genre_counts.most_common(5)

        # Fetch the user's top tracks (short-term data for the last 4 weeks)
        tracks_response = requests.get('https://api.spotify.com/v1/me/top/tracks?limit=50&time_range=short_term', headers=headers)
        tracks_response.raise_for_status()
        tracks_json = tracks_response.json()
        all_tracks = tracks_json.get('items', [])

        # Display only the top 5 tracks in the frontend
        top_5_tracks = all_tracks[:5]

        # Calculate total playback time in minutes for all tracks
        total_playback_ms = sum(track['duration_ms'] for track in all_tracks)
        total_playback_minutes = total_playback_ms / 60000

        # Get track IDs for audio feature analysis
        track_ids = [track['id'] for track in all_tracks]

        avg_danceability = avg_energy = avg_valence = None

        if track_ids:  # Ensure there are track IDs to analyze
            # Fetch audio features for top tracks
            audio_features_response = requests.get(
                'https://api.spotify.com/v1/audio-features',
                headers=headers,
                params={'ids': ','.join(track_ids)}
            )
            audio_features_response.raise_for_status()
            audio_features_json = audio_features_response.json()
            audio_features = audio_features_json.get('audio_features', [])

            # Filter out None values and calculate averages only if audio_features contains valid data
            valid_features = [f for f in audio_features if f is not None]
            if valid_features:
                avg_danceability = sum(f['danceability'] for f in valid_features) / len(valid_features)
                avg_energy = sum(f['energy'] for f in valid_features) / len(valid_features)
                avg_valence = sum(f['valence'] for f in valid_features) / len(valid_features)

        

        # Initialize recommendations
        recommendations = []

        # Get recommendations based on top tracks or artists
        if all_tracks or all_artists:
            seed_artists = ','.join([artist['id'] for artist in all_artists[:2]]) if all_artists else ''
            seed_tracks = ','.join([track['id'] for track in all_tracks[:2]]) if all_tracks else ''

            recommend_params = {
                'seed_artists': seed_artists,
                'seed_tracks': seed_tracks,
                'limit': 5
            }

            recommend_response = requests.get('https://api.spotify.com/v1/recommendations', headers=headers, params=recommend_params)
            recommend_response.raise_for_status()
            recommend_json = recommend_response.json()
            recommendations = recommend_json.get('tracks', [])

    except requests.exceptions.RequestException as e:
        # Enhanced error logging for Spotify API issues
        print(f"Spotify API Request failed: {e}, Status Code: {e.response.status_code if e.response else 'N/A'}, Content: {e.response.text if e.response else 'No response content'}")
        return render(request, 'spotify/error.html', {'message': "Error fetching data from Spotify API."})

    # Render the wraps page with the same user data, top artist, artists, and tracks
    return render(request, 'spotify/wraps.html', {
        'user_data': user_data,
        'top_artist': top_artist,  # Pass the #1 artist separately
        'artists': top_5_artists,  # Pass only top 5 artists to the template
        'tracks': top_5_tracks,  # Pass only top 5 tracks to the template
        'recommendations': recommendations,  # Pass recommendations to the template
        'total_playback_minutes': total_playback_minutes,  # Optional: Pass total playback time
        'top_genres': top_genres,  # Optional: Pass top genres
        'avg_danceability': avg_danceability,  # Optional: Average danceability
        'avg_energy': avg_energy,  # Optional: Average energy
        'avg_valence': avg_valence,  # Optional: Average valence
    })

def refresh_token(request):
    refresh_token = request.session.get('refresh_token')
    if not refresh_token:
        return False

    # Prepare data for token refresh
    refresh_data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET,
    }

    # Send the request to refresh the access token
    response = requests.post(SPOTIFY_TOKEN_URL, data=refresh_data)
    response_json = response.json()

    if 'access_token' in response_json:
        # Update the session with the new access token and expiration time
        request.session['access_token'] = response_json['access_token']
        request.session['token_expires_at'] = time.time() + response_json.get('expires_in', 3600)
        return True
    else:
        # Log the error
        print("Token refresh failed:", response_json)
        return False