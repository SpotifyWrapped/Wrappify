import os
import requests
import time
from django.shortcuts import redirect, render
from collections import Counter
from urllib.parse import urlencode

# Spotify app credentials
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SCOPE = "user-read-private user-read-email user-top-read"

# initial Welcome Page
def login(request):
    return render(request, 'spotify/login.html')

# login page will redirect to spotify login
def loginPage(request):
    auth_params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": SCOPE,
    }
    auth_url = f"{SPOTIFY_AUTH_URL}?{urlencode(auth_params)}"
    return redirect(auth_url)

# refreshes token
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
        'client_secret': SPOTIFY_CLIENT_SECRET,
    }

    token_response = requests.post(SPOTIFY_TOKEN_URL, data=token_data)
    token_json = token_response.json()

    # Print token response for debugging
    print("Token JSON response:", token_json)

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
        # Log the response for debugging
        print("Token exchange response:", token_json)
        return render(request, 'spotify/error.html', {"message": "Token exchange failed."})

# profile view with recommendations
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

        # Initialize recommendations
        recommendations = []

        # Get recommendations based on top tracks or artists
        if all_tracks or artists:
            seed_artists = ','.join([artist['id'] for artist in artists[:2]]) if artists else ''
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

        # Get recommendations based on top tracks or artists
        if tracks or artists:
            seed_artists = ','.join([artist['id'] for artist in artists[:2]]) if artists else ''
            seed_tracks = ','.join([track['id'] for track in tracks[:2]]) if tracks else ''

            recommend_params = {
                'seed_artists': seed_artists,
                'seed_tracks': seed_tracks,
                'limit': 5
            }

            recommend_response = requests.get('https://api.spotify.com/v1/recommendations', headers=headers, params=recommend_params)
            recommend_response.raise_for_status()
            recommend_json = recommend_response.json()
            recommendations = recommend_json.get('tracks', [])

        # Get recommendations based on top tracks or artists
        if tracks or artists:
            seed_artists = ','.join([artist['id'] for artist in artists[:2]]) if artists else ''
            seed_tracks = ','.join([track['id'] for track in tracks[:2]]) if tracks else ''

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
        print(f"Request failed: {e}")  # Log the error
        return render(request, 'spotify/error.html', {'message': "Error fetching data from Spotify API."})

    # Render the profile page with the user data, artists, tracks, and recommendations
    return render(request, 'spotify/profile.html', {
        'user_data': user_data,
        'artists': artists,
        'tracks': top_10_tracks,  # Pass only top 10 tracks to the template
        'recommendations': recommendations,  # Pass recommendations to the template
        'total_playback_minutes': total_playback_minutes,  # Optional: Pass total playback time
        'top_genres': top_genres,  # Optional: Pass top genres
        'avg_danceability': avg_danceability,  # Optional: Average danceability
        'avg_energy': avg_energy,  # Optional: Average energy
        'avg_valence': avg_valence,  # Optional: Average valence
    })
