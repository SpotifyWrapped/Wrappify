import os
import requests
import time
from django.shortcuts import redirect, render
from collections import Counter
from urllib.parse import urlencode

# Spotify app credentials
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SCOPE = "user-read-private user-read-email user-top-read"

# Step 1: Redirect the user to Spotify's login page
def loginPage(request):
    # Define Spotify auth parameters
    auth_params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": SCOPE,
    }
    # Redirect user to Spotify's login page
    auth_url = f"{SPOTIFY_AUTH_URL}?{urlencode(auth_params)}"
    return redirect(auth_url)

# Step 2: Handle the Spotify OAuth callback
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
        'client_secret': os.getenv('SPOTIFY_CLIENT_SECRET'),
    }

    token_response = requests.post(SPOTIFY_TOKEN_URL, data=token_data)
    token_json = token_response.json()

    if 'access_token' in token_json:
        access_token = token_json['access_token']
        refresh_token = token_json.get('refresh_token')
        expires_in = token_json['expires_in']  # Token lifetime in seconds

        # Save tokens and expiration time in session
        request.session['access_token'] = access_token
        request.session['refresh_token'] = refresh_token
        request.session['token_expires_at'] = time.time() + expires_in  # Expiration time

        return redirect('profile')
    else:
        return render(request, 'spotify/error.html', {"message": "Token exchange failed."})

# Step 3: Display the user's profile with their Spotify data (only short-term)
def profile(request):
    access_token = request.session.get('access_token')

    if not access_token:
        return redirect('login')

    headers = {
        'Authorization': f'Bearer {access_token}',
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
        artists = artists_json.get('items', [])

        # Extract and count genres
        genres = []
        for artist in artists:
            genres.extend(artist.get('genres', []))  # Add the artist's genres to the list

        # Use Counter to count occurrences of each genre
        genre_counts = Counter(genres)
        top_genres = genre_counts.most_common(5)

        # Fetch the user's top tracks (short-term data for the last 4 weeks)
        tracks_response = requests.get('https://api.spotify.com/v1/me/top/tracks?limit=50&time_range=short_term', headers=headers)
        tracks_response.raise_for_status()
        tracks_json = tracks_response.json()
        all_tracks = tracks_json.get('items', [])

        # Calculate total playback time in minutes for all tracks
        total_playback_ms = sum(track['duration_ms'] for track in all_tracks)
        total_playback_minutes = total_playback_ms / 60000

        # Display only the top 10 tracks in the frontend
        top_10_tracks = all_tracks[:10]

        # Get track IDs for audio feature analysis
        track_ids = [track['id'] for track in all_tracks]

        # Fetch audio features for top tracks
        audio_features_response = requests.get(
            'https://api.spotify.com/v1/audio-features',
            headers=headers,
            params={'ids': ','.join(track_ids)}
        )
        audio_features_response.raise_for_status()
        audio_features_json = audio_features_response.json()
        audio_features = audio_features_json.get('audio_features', [])

        # Calculate average audio features (mood analysis)
        if audio_features:
            avg_danceability = sum(f['danceability'] for f in audio_features) / len(audio_features)
            avg_energy = sum(f['energy'] for f in audio_features) / len(audio_features)
            avg_valence = sum(f['valence'] for f in audio_features) / len(audio_features)
        else:
            avg_danceability = avg_energy = avg_valence = 0

    except requests.exceptions.RequestException as e:
        return render(request, 'spotify/error.html', {'message': "Error fetching data from Spotify API."})

    # Render the profile page with the user data, top 10 tracks, top genres, total playback time, and mood analysis
    return render(request, 'spotify/profile.html', {
        'user_data': user_data,
        'artists': artists,
        'tracks': top_10_tracks,
        'top_genres': top_genres,
        'total_playback_minutes': f"{total_playback_minutes:.2f}",
        'avg_danceability': f"{avg_danceability:.2f}",
        'avg_energy': f"{avg_energy:.2f}",
        'avg_valence': f"{avg_valence:.2f}"
    })
