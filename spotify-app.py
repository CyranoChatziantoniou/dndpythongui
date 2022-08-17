# -*- coding: utf-8 -*-
"""
Created on Mon May 31 18:34:10 2021

@author: user
"""

# Import libraries
import os
import json
import spotipy
import webbrowser
import spotipy.util as util
from json.decoder import JSONDecodeError

# Get the username from terminal
username = 'crnchtzntn@gmail.com'
scope = 'user-read-private user-read-playback-state user-modify-playback-state'

os.environ['SPOTIPY_CLIENT_ID'] = 'b8b31f8cf6e94d1e868de4f8be23f5a3'
os.environ['SPOTIPY_CLIENT_SECRET'] = '9bb27c4862c74d9f89b168fca2cbaa7e'
os.environ['SPOTIPY_REDIRECT_URI'] = 'https://www.google.nl/'

try:
    token = util.prompt_for_user_token(username, scope)
except (AttributeError, JSONDecodeError):
    os.remove(f".cache-{username}")
    token = util.prompt_for_user_token(username, scope)
    
# Create Spotify object
spotifyObject = spotipy.Spotify(auth=token)

devices = spotifyObject.devices()
# print(json.dumps(devices, sort_keys=True, indent=4))
deviceID = devices['devices'][0]['id']

# Get track information
# track = spotifyObject.current_user_playing_track()
# print(json.dumps(track, sort_keys=True, indent=4))
# artist = track['item']['artists'][0]['name']
# track = track['item']['name']

# if artist !="":
#     print("Currently playing " + artist + " - " + track)

# User information

#%%


while True:

    choice = input("Enter your choice: ")
    
    # Search for artist
    if choice == "0":
        
        # Get search results
        searchResults = spotifyObject.search("Michael Salvatori",1,0,"artist")   
        
        
        # Print artist details
        artist = searchResults['artists']['items'][0]
        artistID = artist['id']
        
        
        # Album details
        trackURIs = []
        trackArt = []
        z = 0
        
        # Extract data from album
        albumResults = spotifyObject.artist_albums(artistID)
        albumResults = albumResults['items']
    
        for item in albumResults:
            print("ALBUM: " + item['name'])
            albumID = item['id']
    
            # Extract track data
            trackResults = spotifyObject.album_tracks(albumID)
            trackResults = trackResults['items']
    
            for item in trackResults:
                print(str(z) + ": " + item['name'])
                trackURIs.append(item['uri'])
                z+=1
            print()
        
        
        # See album art
        while True:
            songSelection = input("Enter a song number to see the album art: ")
            if songSelection == "x":
                break
            trackSelectionList = []
            trackSelectionList.append(trackURIs[int(songSelection)])
            print(trackURIs[int(songSelection)])
            spotifyObject.start_playback(deviceID, None, trackSelectionList)
        
    # End program
    if choice == "1":
        break
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        