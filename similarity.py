
import networkx as nx
import spotipy
#import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random

## TO DO: HOW WILL YOU MAKE IT UNIVERSAL ##
PORT_NUMBER = 8080
SPOTIPY_CLIENT_ID = '5bc2844a6a2849f6a67af0d0e76eda1a'
SPOTIPY_CLIENT_SECRET = '1fe80ea9b0ce464aab9afbb51fbc7800'
SPOTIPY_REDIRECT_URI = 'http://localhost:8080'

mosdef_uri = "spotify:artist:0Mz5XE0kb1GBnbLQm2VbcO"
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

artists = []
f = open("filtered.txt")

for line in f:
    artists.append(line.rstrip())

# the dataset we're using uses names of artists as keys, and we need IDs
def get_id_from_name(name):
    result = spotify.search(q='artist:' + name, type='artist')
    if(result['artists']['items'] == []):
    	return None
    items = result['artists']['items'][0]
    url = items["uri"]
    return(url) 

def get_genre(artist_id):
    artist_object = spotify.artist(artist_id)
    genres = artist_object["genres"]
    print(genres)
    return(genres) 

# full list of related artist
def get_related_artists(artist_id):
    artists = spotify.artist_related_artists(artist_id)['artists']
    ans = [x['uri'] for x in artists]
    return ans

def is_related_to(random_artist, target_artist):
    target_related = get_related_artists(target_artist)
    return (random_artist in target_related)

def five_related(artist_id):
    return get_related_artists(artist_id)[:5]

def sample(artist_list, n):
    sample = random.sample(artist_list, n)
    sample_id = []
    for s in sample:
        sample_id.append(get_id_from_name(s))

    return sample_id

def contest_design(popular_artists, target_artist):
    random_artists_45 = sample(popular_artists, 200)
    related_artists_5 = five_related(target_artist)
    random_artists_45.extend(related_artists_5)
    return random_artists_45

def genre_similarity_scores(target_artist, artist_test_list):
    target_genres = get_genre(target_artist)
    other_artists = contest_design(artist_test_list, target_artist)

    similarity_score = {}
    for artist in other_artists:
        artist_genres = get_genre(artist)
        same_genres = 0
        for genre in artist_genres:
            if(genre in target_genres):
                same_genres += 1

        similarity_score[artist] = same_genres

    return similarity_score

score = genre_similarity_scores(mosdef_uri, artists)

def visualize_similarity(target, similarity_score):
    graph = nx.Graph()

    for k,v in similarity_score:
        graph.add_edge(target, k, weight=v)

    draw_circular(graph)

visualize_similarity(mosdef_uri, score)
