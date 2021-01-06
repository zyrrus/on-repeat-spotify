import json
import requests
from collections import Counter

from ORsecrets import spotify_user_id, On_Repeat_playlist_id
from ORrefresh import Refresh

'''
Take the user's On Repeat playlist by Spotify
and create a new playlist that continually gets
updated, while skipping duplicates 
'''

class SaveSongs:
    def __init__(self):
        self.user_id = spotify_user_id
        self.spotify_token = ""
        self.on_repeat_playlist_id = On_Repeat_playlist_id
        self.on_repeat_tracks = []
        self.new_playlist_name = "Been On Repeat"
        self.new_playlist_id = ""
        self.new_playlist_tracks = []
        self.all_playlists = []
        self.tracks = []
        self.formatted_tracks = ""
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.spotify_token)
        }

    def call_refresh(self):
        #print("Refreshing token...")

        refresh_caller = Refresh()
        self.spotify_token = refresh_caller.refresh()

        self.headers["Authorization"] = "Bearer {}".format(self.spotify_token)

    def get_songs_from_on_repeat(self):
        #print("Finding songs in On Repeat...")

        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(self.on_repeat_playlist_id)
        response = requests.get(query, headers=self.headers)
        response_json = response.json()

        #create comma separated list of track ids
        for track in response_json["items"]:
            self.on_repeat_tracks.append(track["track"]["uri"])
        
        return self.on_repeat_tracks

    def get_songs_from_existing_playlist(self):
        #print("Finding songs in New Playlist...")

        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(self.new_playlist_id)
        response = requests.get(query, headers=self.headers)
        response_json = response.json()

        #create comma separated list of track ids
        for track in response_json["items"]:
            self.new_playlist_tracks.append(track["track"]["uri"])

        return self.new_playlist_tracks

    def create_new_playlist(self):
        #print("Creating new playlist...")

        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.user_id)
        requests_body = json.dumps({
            "name": self.new_playlist_name,
            "public": "true"
        })

        response = requests.post(query, data=requests_body, headers=self.headers)
        response_json = response.json()

        return response_json["id"]

    def update_playlist(self):
        '''
        get list of songs currently in playlist,
        merge the two lists of songs skipping duplicates,
        replace songs in playlist
        '''
        #print("Updating existing playlist...")
        
        #join track lists
        self.tracks = list((Counter(self.get_songs_from_on_repeat())-Counter(self.get_songs_from_existing_playlist())).elements())
        
        for track in self.tracks:
            self.formatted_tracks += track + ","
        self.formatted_tracks = self.formatted_tracks[:-1]
        

        query = "https://api.spotify.com/v1/playlists/{}/tracks?uris={}".format(self.new_playlist_id, self.formatted_tracks)
        response = requests.post(query, headers=self.headers)
        

    def run(self):
        '''
        get list of user playlists,
        try to find Been On Repeat,
        if it exists: update
        else: create new
        '''

        #refresh token
        self.call_refresh()

        #get list of user playlists
        #print("Getting playlists...")
        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.user_id)

        response = requests.get(query, headers=self.headers)
        response_json = response.json()

        for playlist in response_json["items"]:
            self.all_playlists.append(playlist["name"])

        #check if playlist already exists
        if self.new_playlist_name not in self.all_playlists:
            #print("it does not exist")
            self.new_playlist_id = self.create_new_playlist()
        else:
            #print("it does exist")
            correct_playlist = response_json["items"][self.all_playlists.index(self.new_playlist_name)]
            self.new_playlist_id = correct_playlist["id"]
            #get songs in this playlist
            
        #print("adding songs...")
        self.update_playlist()
        print("DONE")



a = SaveSongs()
a.run()