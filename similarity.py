
import networkx as nx
import spotipy
#import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random
import matplotlib.pyplot as plt
import numpy as np


## TO DO: HOW WILL YOU MAKE IT UNIVERSAL ##
PORT_NUMBER = 8080
SPOTIPY_CLIENT_ID = '5bc2844a6a2849f6a67af0d0e76eda1a'
SPOTIPY_CLIENT_SECRET = '1fe80ea9b0ce464aab9afbb51fbc7800'
SPOTIPY_REDIRECT_URI = 'http://localhost:8080'


mosdef_uri = "spotify:artist:0Mz5XE0kb1GBnbLQm2VbcO"
taylor_swift_uri = "spotify:artist:06HL4z0CvFAxyc27GXpf02"
johnny_cash_uri = "spotify:artist:6kACVPfCOnqzgfEF5ryl0x"
kanye_uri = "spotify:artist:5K4W6rqBFWDnAN6FQUkS6x"
meg_thee_uri = "spotify:artist:181bsRPaVXVlUKXrxwZfHK"
phoebe_bridgers_uri = "spotify:artist:1r1uxoy19fzMxunt3ONAkG"
beatles_uri = "spotify:artist:3WrFJ7ztbogyGnTHbHJFl2"
velvet_uri = "spotify:artist:1nJvji2KIlWSseXRSlNYsC"
kidcudi_uri = "spotify:artist:0fA0VVWsXO9YnASrzqfmYu"
clora_bryant = "spotify:artist:3MmQAaWO06tTOnbUhfDAfF"

spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

artists = []
f = open("filtered_artists.txt")

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

#takes in ID and returns list of genres for that artist
def get_genre(artist_id):
    artist_object = spotify.artist(artist_id)
    genres = artist_object["genres"]
    return(genres) 

#takes in ID and returns full list of related artist
def get_related_artists(artist_id):
    artists = spotify.artist_related_artists(artist_id)['artists']
    ans = [x['uri'] for x in artists]
    return ans

def get_popularity(artist_id):
    artist_object = spotify.artist(artist_id)
    popularity = artist_object["popularity"]
    return(popularity) # a score out of 100



# Avg danceability score of an artist's top 10 tracks
def avg_dance(artist_id):
    results = spotify.artist_top_tracks(artist_id)
    # ids of top 10 tracks
    track_ids = [r['uri'] for r in results['tracks']]
    # features of the above tracks
    feats = spotify.audio_features(track_ids)
    danceability_scores = []
    for f in feats:
        try:
            danceability_scores.append(f['danceability'])
        except TypeError:
            pass
        try:
            return round(sum(danceability_scores)/len(danceability_scores), 3) # avg score
        except ZeroDivisionError:
            return 10000


#takes in two artist IDs and returns true if related and false if not
def are_related(random_artist_id, target_artist_id):
    random_related = get_related_artists(random_artist_id)
    target_related = get_related_artists(target_artist_id)
    return (random_artist_id in target_related or target_artist_id in random_related)

#takes artist ID and returns list of five related artists
def five_related(artist_id):
    return get_related_artists(artist_id)[:5]

#gets the whole artist list and sample size n, and returns a sample of n artists
def sample(artist_list, n):
    sample = random.sample(artist_list, n)
    sample_id = []
    for s in sample:
        sample_id.append(s)
    return sample_id

#returns a list of 5 related artists and n unrelated artists
def contest_design(artist_list, target_artist, n):
    random_artists = sample(artist_list, n)
    related_artists_5 = five_related(target_artist)
    random_artists.extend(related_artists_5)
    return random_artists

#takes in target artist, the list of all artists, and a sample size n
#returns a similarity score as a dictionary, between the artist and 
#all of the other artists in the sample
def genre_similarity_scores(target_artist, artist_list):
    target_genres = get_genre(target_artist)

    similarity_score = {}
    for artist in artist_list:
        artist_genres = get_genre(artist)
        same_genres = 0
        for genre in artist_genres:
            if(genre in target_genres):
                same_genres += 1

        similarity_score[artist] = same_genres/len(target_genres)

    return similarity_score

def pop_sim_scores(target_artist, other_artists):
    target_pop = get_popularity(target_artist)
    
    similarity_score = {}
    for artist in other_artists:
        artist_pop = get_popularity(artist)
        
        similarity_score[artist] = (100-abs(target_pop - artist_pop))/100
    
    return similarity_score



# How similar are Artist1 and Artist2 in terms of danceability
def dance_sim_scores(target_artist, other_artists):
    target_dance = avg_dance(target_artist)
    
    similarity_score = {}
    for artist in other_artists:
        artist_dance = avg_dance(artist)
        
        similarity_score[artist] = 1-abs(target_dance-artist_dance)
        
    return similarity_score




#takes the similarity score dictionary returned by genre similarity scores
#and returns the top 5 highest scoring artists
def get_top_five_similar_artists(similarity_score):
    sorted_similar = sorted(similarity_score.items(), key=lambda x: x[1], reverse=True)
    sorted_similar = sorted_similar[:5]
    top_5 = []
    for k,v in sorted_similar:
        top_5.append(k)

    return top_5

#compares the prediction top 5 with the actual top 5 and returns a score
def scoring_comp(target_artist, similarity_score):
    top_five = get_top_five_similar_artists(similarity_score)
    real_top_five = five_related(target_artist)

    score = 0

    for a in top_five:
        if(a in real_top_five):
            score += 1

    return score

#takes in a target artist, list of all artists and a similarity score dictionary
#constructs a graph wherein the target node is black, the spotify related artists are red
#and the remainder are blue. returns a graph with edges between target node and nodes
#we predict are related
def visualize_similarity_guessed(target, artists, similarity_score):
    graph = nx.Graph()
    color_map = []

    related = five_related(target)

    graph.add_node(target)
    graph.add_nodes_from(artists)

    for k,v in similarity_score.items():
        if(v > 0):
            graph.add_edge(target, k, weight=v, length = 10)

    for node in graph.nodes():
        if(node in related):
            color_map.append('red')
        elif(node == target):
            color_map.append('black')
        else:
            color_map.append('blue')

    nx.draw(graph, node_color=color_map, node_size = 1)
    plt.show()



test_artists = [
mosdef_uri,
taylor_swift_uri,
johnny_cash_uri,
kanye_uri,
meg_thee_uri,
phoebe_bridgers_uri,
beatles_uri, 
velvet_uri,
kidcudi_uri,
clora_bryant 
]







# Given <ARTIST> with sample size <n>
# Return my score out of 5
def test_me_genre(target_artist, sample_list):
    sim_score = genre_similarity_scores(target_artist, sample_list)
    my_score = scoring_comp(target_artist, sim_score)
    return my_score

# Given <ARTIST> with sample size <n>
# Return my score out of 5
def test_me_pop(target_artist, sample_list):
    sim_score = pop_sim_scores(target_artist, sample_list)
    my_score = scoring_comp(target_artist, sim_score)
    return my_score

def test_me_dance(target_artist, sample_list):
    sim_score = dance_sim_scores(target_artist, sample_list)
    my_score = scoring_comp(target_artist, sim_score)
    return my_score



# average my scores over <iter> iterations 
# where a single iteration has sample size n

def run_experiment_genre_only(artists, artist, iterations, sample_size):
    my_sample = contest_design(artists, artist, sample_size)

    my_scores = []
    for i in range(iterations):
        print("iteration number: ", i)
        my_scores.append(test_me_genre(artist, my_sample))
    avg = sum(my_scores) / len(my_scores)
    return avg

def run_experiment_genre_and_pop(artists, artist, iterations, sample_size):
    my_sample = contest_design(artists, artist, sample_size)

    my_scores = []
    for i in range(iterations):
        print("iteration number: ", i)
        my_scores.append((test_me_genre(artist, my_sample) + 
                          test_me_pop(artist, my_sample))/2)
    avg = sum(my_scores) / len(my_scores)
    return avg

def run_experiment_all_3(artists, artist, iterations, sample_size):
    my_sample = contest_design(artists, artist, sample_size)

    my_scores = []
    for i in range(iterations):
        print("iteration number: ", i)
        my_scores.append(
            (test_me_genre(artist, my_sample) + 
             test_me_pop(artist, my_sample) +
             test_me_dance(artist, my_sample)) / 3)
    avg = sum(my_scores) / len(my_scores)
    return avg



def one_experiment(testset, full_list, iters, sample_size):
    score1 = 0
    score2 = 0
    score3 = 0

    print("STARTED EXPERIMENT -- artists:  {0}, iterations: {1}, sample size: {2}----\n".format(len(testset), iters, sample_size))


    for a in testset:
        print("testing artist: ", name(a), '\n')
        score1 += run_experiment_genre_only(full_list, a, iters, sample_size)
        score2 += run_experiment_genre_and_pop(full_list, a, iters, sample_size)
        score3 += run_experiment_all_3(full_list, a, iters, sample_size)

    print("---Average scores for {0} artists, over {1} iterations with a sample size of {2}----\n".format(len(testset), iters, sample_size))

    print("Experiment with only genre considered:  ", score1/len(testset))
    print("Experiment with genre and popularity considered: ", score2/len(testset))
    print("Experiment with genre, popularity and average danceability of artist's top 5 songs considered: ", score3/len(testset))




one_experiment(test_artists, artists, 10, 50)





# #scores how our function performs with various sample sizes and plots it
# sample_size = [50, 250, 500]
# scores_one = []
# scores_two = []
# scores_three = []

# for i in range(10): # Number of iterations
#     print("initiating round " + str(i))
#     iteration_one = []
#     iteration_two = []
#     iteration_three = []
#     for j in sample_size:
#         other_artists, similarity_score_one = genre_similarity_scores(mosdef_uri, artists, j-5)
#         iteration_one.append(scoring_comp(mosdef_uri,  similarity_score_one))
#         other_artists, similarity_score_two = pop_sim_scores(mosdef_uri, other_artists, similarity_score_one)
#         iteration_two.append(scoring_comp(mosdef_uri,  similarity_score_two))
#         other_artists, similarity_score_three = dance_sim_score(mosdef_uri, other_artists, similarity_score_two)
#         iteration_three.append(scoring_comp(mosdef_uri,  similarity_score_three))
#     scores_one.append(iteration_one)
#     scores_two.append(iteration_two)
#     scores_three.append(iteration_three)


# results_one = [0]*len(sample_size) #Populate a list of zeros the size of number of
# results_two = [0]*len(sample_size) #sample sizes tested 
# results_three = [0]*len(sample_size)

# for i in range(len(scores_one)):
#     for j in range(len(scores_one[i])):
#         results_one[j] += scores_one[i][j]
#         results_two[j] += scores_two[i][j]
#         results_three[j] += scores_three[i][j]


# average_results_one = np.divide(results_one, len(scores_one))
# average_results_two = np.divide(results_two, len(scores_two))
# average_results_three = np.divide(results_three, len(scores_three))

# plt.plot(sample_size, average_results_one.tolist())
# plt.ylim(0,5)
# plt.title('Mos Def - Similarity scoring (genre only)')
# plt.xlabel('Sample size')
# plt.ylabel('Average of Correctly guessed similar artists')
# plt.show()

# plt.plot(sample_size, average_results_one.tolist())
# plt.ylim(0,5)
# plt.title('Mos Def - Similarity scoring (genre and popularity)')
# plt.xlabel('Sample size')
# plt.ylabel('Average of Correctly guessed similar artists') 
# plt.show()

# plt.plot(sample_size, average_results_one.tolist())
# plt.ylim(0,5)
# plt.title('Mos Def - Similarity scoring (genre, popularity, and danceability)')
# plt.xlabel('Sample size')
# plt.ylabel('Average of Correctly guessed similar artists')
# plt.show()

