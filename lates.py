
import networkx as nx
import spotipy
#import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials



## TO DO: HOW WILL YOU MAKE IT UNIVERSAL ##
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

# full list of related artist
def get_related_artists(artist_id):
    artists = spotify.artist_related_artists(artist_id)['artists']
    ans = [x['uri'] for x in artists]
    return ans


def is_related_to(random_artist, target_artist):
    target_related = get_related_artists(target_artist)
    return (random_artist in target_related)


def five_related(artist):
    return get_related_artists(artist)[:5]


# TO DO : GET THIS TO BE UNIVERSAL
f = open("./data_by_artists.csv")

header = f.readline()

headerList = header.strip("\n").split(",")

artistI = headerList.index("artists")

artist_list = []

for line in f.readlines():
    if line.count(",") == header.count(","):
        line = line.split(",")
        artist_list.append(line[artistI])
    elif line.count(",") >= header.count(","):
        commaCount = line.count(",") - header.count(",")
        line = line.split(",")
        newLine = [",".join(line[0:commaCount+1])]
        newLine.extend(line[commaCount+1:len(line)-1])
        artist_list.append(newLine[artistI])
        

f.close()

def sample1000(artistNameList):
    import random
    indexList = []
    sample = []
    for i in range(1000):
        num = random.randint(0, len(artistNameList))
        while num in indexList:
            num = random.randint(0, len(artistNameList))
        indexList.append(num)
        sample.append(artistNameList[num])
    return sample

def sample45(sample1000):
    import random
    indexList = []
    sample = []
    for i in range(45):
        num = random.randint(0, len(sample1000))
        while num in indexList:
            num = random.randint(0, len(sample1000))
        indexList.append(num)
        sample.append(sample1000[num])
    return sample

popular_artists = [] #Lists of artists with five related artists

# for artist in artist_list:
#     related = get_related_artists(id(artist))
#     if len(related) >= 5:
#         popular_artists.append(artist)


# def contest_design(popular_artists, target_artist):
#     random_artists_45 = sample45(sample1000(popular_artists))
#     related_artists_5 = get_five_related(target_artist)
#     random_artists_45.extend(related_artists_5)
#     return random_artists_45
    
print("weird_al_id : ", id('Karaoke - Yankovic, "Weird Al"'))

