import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

# Initialize variables for storing data
tracks_df = pd.DataFrame()
ids = []
years = [2000, 2001]
songs_list = []
artists_list = []
audio_features = []

# Spotify API credentials
CLIENT_ID = ""
CLIENT_SECRET = ""

# Setup Spotify client with credentials
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager, requests_timeout=10)


def construct_audio_features_df(results):
    """
    Extract audio features from the Spotify API response and structure them into a dictionary.
    """
    audio_data = {
        'id': results['id'],
        'danceability': results['danceability'],
        'energy': results['energy'],
        'key': results["key"],
        'loudness': results["loudness"],
        'mode': results['mode'],
        'speechiness': results['speechiness'],
        'acousticness': results['acousticness'],
        'instrumentalness': results['instrumentalness'],
        'liveness': results['liveness'],
        'valence': results['valence'],
        'tempo': results['tempo'],
        'time_signature': results['time_signature'],
    }
    return audio_data


def get_audio_features(track_ids, chunk_size):
    """
    Fetch audio features for a list of track IDs in chunks to manage API rate limits efficiently.
    """
    print(f'Number of tracks: {len(track_ids)}')
    for i in range(0, len(track_ids), chunk_size):
        try:
            print(f'Audio_Features_Chunk: {i}')
            track_ids_chunk = track_ids[i:i + chunk_size]
            features = sp.audio_features(track_ids_chunk)
            for track_features in features:
                track_features_dict = construct_audio_features_df(track_features)
                audio_features.append(track_features_dict)
        except Exception:
            continue


def get_genre(artist_ids_list, chunk_size):
    """
    Fetch genres for a list of artist IDs in chunks to manage API rate limits efficiently.
    """
    artists_df = pd.DataFrame()
    print(f'Number of Artists: {len(artist_ids_list)}')
    for i in range(0, len(artist_ids_list), chunk_size):
        try:
            print(f'Artist_Chunk: {i}')
            artist_ids_chunk = artist_ids_list[i:i + chunk_size]
            artists_res = sp.artists(artist_ids_chunk)
            for artist_res in artists_res['artists']:
                artist_genre = {'artist_id': artist_res['id'], 'artist_genres': artist_res['genres']}
                artists_list.append(artist_genre)
        except Exception:
            continue
    return artists_df


def get_unique_random_searches(n):
    """
    Generate a set of unique random search strings to diversify the search queries.
    """
    characters = 'abcdefghijklmnopqrstuvwxyz'
    random_searches = set()
    while len(random_searches) < n:
        random_character = random.choice(characters)
        random_search_str = random_character + '*'
        random_searches.add(random_search_str)
    return random_searches


# Fetch and store track information by year
for year in range(2010, 2024, 1):
    print(f'--------------Year: {year}')
    unique_searches = get_unique_random_searches(3)

    for random_search in unique_searches:
        print(random_search)
        tracks = sp.search(q=f'year:{year} track:{random_search}', type='track', limit=50)
        while tracks:
            for track in tracks['tracks']['items']:
                songs_data = {
                    'id': track['id'],
                    'song_name': track['name'],
                    'artist_name': track['artists'][0]['name'],
                    'artist_id': track['artists'][0]['id'],
                    'preview_url': track['preview_url'],
                    'release_date': track['album']['release_date'],
                    'song_link': track['external_urls']['spotify'],
                    'song_duration': track['duration_ms'],
                    'song_popularity': track['popularity']
                }
                songs_list.append(songs_data)
            tracks = sp.next(tracks['tracks']) if tracks['tracks']['next'] else None

# Create DataFrame from collected song data and remove duplicates
songs_df = pd.DataFrame(songs_list).drop_duplicates(subset='id')

# Save the songs DataFrame to a CSV file
print('----------songs_df.shape')
print(songs_df.shape)
songs_df.to_csv('SongsData.csv', index=False)

# Fetch genres for unique artist IDs and save to CSV
artist_ids_unique = songs_df['artist_id'].unique().tolist()
get_genre(artist_ids_unique, 50)
df_genres = pd.DataFrame(artists_list)
print('----------df_genres.shape')
print(df_genres.shape)
df_genres.to_csv('GenresData.csv', index=False)

# Fetch audio features for tracks and save to CSV
get_audio_features(songs_df['id'], 50)
df_audios = pd.DataFrame(audio_features)
print('----------df_audios.shape')
print(df_audios.shape)
df_audios.to_csv('AudioFeaturesData.csv', index=False)

# Merge DataFrames to create a final dataset and save to CSV
df_full_track_info = pd.merge(songs_df, df_audios, how='left', on='id')
df_full_track_info = pd.merge(df_full_track_info, df_genres, how='left', on='artist_id')
print('----------df_full_track_info.shape')
print(df_full_track_info.shape)
df_full_track_info.to_csv('FullTrackInfo.csv', index=False)
