import os
import requests
import time
from django.shortcuts import redirect, render
from urllib.parse import urlencode

# Spotify app credentials
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

# Updated Spotify scopes to include user-top-read
SCOPE = "user-read-private user-read-email user-top-read"

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

def spotify_callback(request):
    code = request.GET.get('code')

    if not code:
        return render(request, 'spotify/error.html', {"message": "Authorization failed."})

    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': os.getenv('SPOTIFY_CLIENT_SECRET'),
    }

    token_response = requests.post(SPOTIFY_TOKEN_URL, data=token_data)
    token_json = token_response.json()

    # Print token response for debugging
    print("Token JSON response:", token_json)

    if 'access_token' in token_json:
        access_token = token_json['access_token']
        refresh_token = token_json.get('refresh_token')  # Optional
        expires_in = token_json['expires_in']  # Token lifetime in seconds

        # Save tokens and expiration time in session
        request.session['access_token'] = access_token
        request.session['refresh_token'] = refresh_token
        request.session['token_expires_at'] = time.time() + expires_in  # Expiration time

        return redirect('profile')  # Redirect to profile after successful login
    else:
        return render(request, 'spotify/error.html', {"message": "Token exchange failed."})

def get_user_profile(request):
    access_token = request.session.get('access_token')

    if not access_token:
        return redirect('login')

    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    user_profile_response = requests.get('https://api.spotify.com/v1/me', headers=headers)
    user_data = user_profile_response.json()

    return render(request, 'spotify/profile.html', {'user_data': user_data})

def profile(request):
    access_token = request.session.get('access_token')

    # Check if access token is available
    if not access_token:
        print("No access token, redirecting to login.")
        return redirect('login')

    print("Access token found, proceeding to fetch user data.")

    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    try:
        # Fetch user profile information
        user_profile_response = requests.get('https://api.spotify.com/v1/me', headers=headers)
        user_profile_response.raise_for_status()
        user_data = user_profile_response.json()

        print("User profile data fetched successfully.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Spotify API: {e}")
        return render(request, 'spotify/profile.html', {
            'user_data': None,
        })

    return render(request, 'spotify/profile.html', {
        'user_data': user_data,
    })
