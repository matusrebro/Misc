"""

Spotify user data scraper

"""

import selenium.webdriver as webdriver
try:
    import urllib.request, urllib.error
    import urllib.parse as urllibparse
except ImportError:
    import urllib as urllibparse
import time
import requests
import base64
import numpy as np
import matplotlib.pyplot as plt


# client id and secret from registered spotify app
# here they are loaded from numpy binary file
client_id, client_secret = np.load('creds.npy')

# path to gecko driver (geckodriver.exe) for selenium firefox usage
firePath = "geckodriver.exe"

# --- Getting code from user ---

def get_user_code(client_id, client_secret, firePath):
    
    OAUTH_AUTHORIZE_URL = 'https://accounts.spotify.com/authorize'
    
    payload = {'client_id': client_id,
               'response_type': 'code',
               'redirect_uri': 'https://localhost/callback/',
               'scope': 'user-top-read'}
    urlparams = urllibparse.urlencode(payload)

    url="%s?%s" % (OAUTH_AUTHORIZE_URL, urlparams)

    browser = webdriver.Firefox(executable_path=firePath)
    browser.get(url) 


    while 'code=' not in browser.current_url:
        print('waiting for user to accept')
        time.sleep(5)

    resultURL = browser.current_url
    code=resultURL.split('code=')[1]
    browser.close()
    
    return code


code = get_user_code(client_id, client_secret, firePath)

# --- Using code to get token ---
def get_user_token(code):
    
    OAUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'
    
    payload = {'grant_type': 'authorization_code',
               'code': code,
               'redirect_uri': 'https://localhost/callback/'}
    
    auth_header = base64.b64encode(str(client_id + ':' + client_secret).encode())
    headers = {'Authorization': 'Basic %s' % auth_header.decode()}
    
    response = requests.post(OAUTH_TOKEN_URL, data=payload,
                headers=headers, verify=True)
    
    token_info = response.json()

    return token_info

token_info = get_user_token(code)

"""
time_range: 

long_term - whole user's history
medium_term - approx. last 6 months
short_term - approx. last 4 weeks
"""

# --- Top artists --- 
# --- Maximum amount of get-able artists is 99
def get_top_artists(token_info,limit=50,time_range='long_term'):

    TOP_ARTISTS_URL = 'https://api.spotify.com/v1/me/top/artists'
    
    auth_header = token_info['access_token']
    headers = {'Authorization': 'Bearer %s' % auth_header}
    
    limit_max = 50
    offset_max = 49 # request returns empty list when  offset>=50
    limit = np.min([limit,limit_max+offset_max]) # due to the offset limit the maximum amount that can be requested is 99
    offsets = np.arange(0,int(np.ceil(limit/limit_max)))*offset_max
    limits = np.zeros_like(offsets)
    
    limits[0] = np.min([limit,limit_max])
    for k in range(1,len(offsets)):
        limits[k] = np.min([limit + 1 - limit_max * k, limit_max])
    
    top_artists_info = []
    for k in range(len(offsets)):
        
        payload = {'limit': limits[k],
                   'time_range': time_range,
                   'offset' : offsets[k]
                   }
        
        urlparams = urllibparse.urlencode(payload)
        url="%s?%s" % (TOP_ARTISTS_URL, urlparams)
        
        response = requests.get(url,# data=payload,
                    headers=headers, verify=True)
        
        top_artists_info0=response.json()['items']
        
        index = 0
        for item in top_artists_info0:
            if index==0 and k==1:
                pass
            else:
                top_artists_info.append(item)
            index+=1
        
    return top_artists_info


top_artists_info = get_top_artists(token_info,limit=66,time_range='long_term')

artist_names = [artist['name'] for artist in top_artists_info]






# --- Top songs --- 
# --- Maximum amount of get-able tracks is 99
def get_top_tracks(token_info,limit=50,time_range='long_term'):
    TOP_SONGS_URL = 'https://api.spotify.com/v1/me/top/tracks'
    
    auth_header = token_info['access_token']
    
    headers = {'Authorization': 'Bearer %s' % auth_header}
    
    limit_max = 50
    offset_max = 49 # request returns empty list when  offset>=50
    limit = np.min([limit,limit_max+offset_max]) # due to the offset limit the maximum amount that can be requested is 99
    offsets = np.arange(0,int(np.ceil(limit/limit_max)))*offset_max
    limits = np.zeros_like(offsets)
    
    limits[0] = np.min([limit,limit_max])
    for k in range(1,len(offsets)):
        limits[k] = np.min([limit + 1 - limit_max * k, limit_max])    
    
    top_songs_info = []
    for k in range(len(offsets)):
        
        payload = {'limit': limits[k],
                   'time_range': time_range,
                   'offset' : offsets[k]
                   }
        
        urlparams = urllibparse.urlencode(payload)
        url="%s?%s" % (TOP_SONGS_URL, urlparams)
        
        response = requests.get(url,# data=payload,
                    headers=headers, verify=True)
        
        top_songs_info0=response.json()['items']
        
        index = 0
        for item in top_songs_info0:
            if index==0 and k==1:
                pass
            else:
                top_songs_info.append(item)
            index+=1
        
    return top_songs_info

top_songs_info = get_top_tracks(token_info,limit=66,time_range='long_term')


song_names = [song['name'] for song in top_songs_info]
song_ids = [song['id'] for song in top_songs_info]

song_popularity = [song['popularity'] for song in top_songs_info]
song_explicit = [song['explicit'] for song in top_songs_info]

# --- Top songs audio features --- 
AUDIO_FEATURES_URL = 'https://api.spotify.com/v1/audio-features/?ids='

auth_header = token_info['access_token']
headers = {'Authorization': 'Bearer %s' % auth_header}

url=AUDIO_FEATURES_URL+','.join(song_ids)

response = requests.get(url,# data=payload,
            headers=headers, verify=True)

audio_features_info=response.json()['audio_features']

audio_features_danceability = [audio_feature['danceability'] for audio_feature in audio_features_info]
audio_features_energy = [audio_feature['energy'] for audio_feature in audio_features_info]
audio_features_tempo = [audio_feature['tempo'] for audio_feature in audio_features_info]
audio_features_time_signature = [audio_feature['time_signature'] for audio_feature in audio_features_info]
audio_features_valence = [audio_feature['valence'] for audio_feature in audio_features_info]
audio_features_duration_ms = [audio_feature['duration_ms'] for audio_feature in audio_features_info]
audio_features_speechiness = [audio_feature['speechiness'] for audio_feature in audio_features_info]


# --- histogram plot
plt.figure()

plt.subplot(331)
plt.title('Duration [min]')
plt.hist(np.round(np.asarray(audio_features_duration_ms)/1000/60))

plt.subplot(332)
plt.title('Tempo [bpm]')
plt.hist(np.round(audio_features_tempo,-1))

plt.subplot(333)
plt.title('Time Signature [beats in bar]')
plt.hist(audio_features_time_signature)

plt.subplot(334)
plt.title('Energy')
plt.hist(np.round(audio_features_energy,2))

plt.subplot(335)
plt.title('Danceability')
plt.hist(np.round(audio_features_danceability,2))

plt.subplot(336)
plt.title('Valence')
plt.hist(np.round(audio_features_valence,2))

plt.subplot(337)
plt.title('Speechiness')
plt.hist(np.round(audio_features_speechiness,2))

plt.subplot(338)
plt.title('Popularity')
plt.hist(np.round(song_popularity,-1))

plt.subplot(339)
plt.title('Explicit')
plt.hist([int(b) for b in song_explicit])

plt.tight_layout()