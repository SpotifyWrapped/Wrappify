// Fetch function to make API calls to Spotify
async function fetchSpotifyApi(endpoint, method = 'GET', accessToken) {
    const response = await fetch(`https://api.spotify.com/${endpoint}`, {
        headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
        },
        method,
    });

    if (!response.ok) {
        throw new Error(`Spotify API error: ${response.statusText}`);
    }

    return await response.json();
}

// Fetch and display user's top artists
async function displayTopArtists(accessToken) {
    try {
        const artistsData = await fetchSpotifyApi('v1/me/top/artists?limit=5', 'GET', accessToken);
        const artistList = document.getElementById('top-artists');
        
        // Clear loading message
        artistList.innerHTML = '';

        if (artistsData.items.length === 0) {
            artistList.innerHTML = `<li>No top artists available.</li>`;
            return;
        }
        
        artistsData.items.forEach(artist => {
            const listItem = document.createElement('li');
            listItem.innerHTML = `
                <img src="${artist.images[0].url}" alt="${artist.name}" width="100">
                <p>${artist.name}</p>
            `;
            artistList.appendChild(listItem);
        });

    } catch (error) {
        console.error('Error fetching top artists:', error);
        const artistList = document.getElementById('top-artists');
        artistList.innerHTML = `<li>Error loading top artists.</li>`;
    }
}

// Fetch and display user's top tracks
async function displayTopTracks(accessToken) {
    try {
        const tracksData = await fetchSpotifyApi('v1/me/top/tracks?limit=5', 'GET', accessToken);
        const trackList = document.getElementById('top-tracks');
        
        // Clear loading message
        trackList.innerHTML = '';

        if (tracksData.items.length === 0) {
            trackList.innerHTML = `<li>No top tracks available.</li>`;
            return;
        }

        tracksData.items.forEach(track => {
            const listItem = document.createElement('li');
            listItem.innerHTML = `
                <img src="${track.album.images[0].url}" alt="${track.name}" width="100">
                <p>${track.name} by ${track.artists.map(artist => artist.name).join(', ')}</p>
            `;
            trackList.appendChild(listItem);
        });

    } catch (error) {
        console.error('Error fetching top tracks:', error);
        const trackList = document.getElementById('top-tracks');
        trackList.innerHTML = `<li>Error loading top tracks.</li>`;
    }
}

// Initialize functions to fetch and display data
function initializeProfilePage(accessToken) {
    displayTopArtists(accessToken);
    displayTopTracks(accessToken);
}

// Make sure this script runs only after the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    const accessToken = document.getElementById('access-token').value;
    
    if (accessToken) {
        initializeProfilePage(accessToken);
    } else {
        console.error('Access token not found. Unable to fetch Spotify data.');
    }
});
