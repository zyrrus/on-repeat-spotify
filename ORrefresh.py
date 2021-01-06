import json
import requests

from ORsecrets import refresh_token, base_64

class Refresh:
    def __init__(self):
        self.refresh_token = refresh_token
        self.base_64 = base_64

    def refresh(self):
        query = "https://accounts.spotify.com/api/token"
        response = requests.post(query, 
            data={"grant_type": "refresh_token", "refresh_token": self.refresh_token},
            headers={"Authorization": "Basic " + self.base_64})
        
        response_json = response.json()
        return response_json["access_token"]

a = Refresh()
a.refresh()