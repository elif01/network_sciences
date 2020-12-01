import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


PORT_NUMBER = 8080
SPOTIPY_CLIENT_ID = '5bc2844a6a2849f6a67af0d0e76eda1a'
SPOTIPY_CLIENT_SECRET = '1fe80ea9b0ce464aab9afbb51fbc7800'
SPOTIPY_REDIRECT_URI = 'http://localhost:8080'

mosdef_uri = "spotify:artist:0Mz5XE0kb1GBnbLQm2VbcO"
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())


# the dataset we're using uses names of artists as keys, and we need IDs
def id(name):
    result = spotify.search(q='artist:' + name, type='artist')
    items = result['artists']['items'][0]
    url = items["uri"]
    return(url) 
    #prefix = "spotify:artist:"
    #print(url[len(prefix):])


def get_related_artists(artist_id):
    artists = spotify.artist_related_artists(artist_id)['artists']
    ans = [x['uri'] for x in artists]
    return ans

def are_related(a1, a2):
    a1_related = get_related_artists(a1)
    a2_related = get_related_artists(a2)
    
    return (a2 in a1_related or a1 in a2_related)

def five_related(artist):
    return get_related_artists(artist)[:5]



print(five_related(id('thom yorke')))


#def are_related(a1, a2):
    


# FOR CONVENIENCE
# radiohead =    spotify:artist:4Z8W4fKeB5YxbusRsdQVPb
# mosdef =       spotify:artist:0Mz5XE0kb1GBnbLQm2VbcO
#
#
#
#
