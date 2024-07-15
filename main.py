import spotipy
import os
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()
ENV = os.getenv('TEST')
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

#TODO Create user data class

def user_auth():
    # Defines user authentication permissions
    scope = 'playlist-modify-public '
    scope += 'playlist-modify-private '
    scope += 'playlist-read-private '
    scope += 'user-modify-playback-state '
    scope += 'user-library-read '
    scope += 'user-read-currently-playing '
    scope += 'user-follow-read '
    scope += 'user-library-modify '
    scope += 'user-read-private '
    scope += 'user-top-read'

    # Creates spotify object with user credentials/auth tokens using scope
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    return spotify


def search_song(song_title: str, artist: str, explicit:bool, ask:bool, spotify) -> str:
    # query = 'remaster%2520track%3ADoxy%2520artist%3AMiles%2520Davis'
    # query = 'track%20smart%20artist%20lesserafim'
    # Create query based on input parameters inline with Spotify API format where '%20' represents a space in HTML
    song_title = song_title.replace(' ', '%20')
    artist = artist.replace(' ', '%20')
    query = 'track%20'+song_title+'%20artist%20'+artist

    # Query songs
    search = spotify.search(q=query, limit=1, type='track')
    # playlist = spotify.playlist(playlist_id)

    # playlist_uri = playlist["uri"]

    # track_spotify_url = search["tracks"]["items"][0]["external_urls"]["spotify"]

    # Checks if songs are explicit
    if explicit:
        track_uri = search["tracks"]["items"][0]["uri"]
    else:
        if search["tracks"]["items"][0]["explicit"] == False:
            track_uri = search["tracks"]["items"][0]["uri"]
        else:
            query_song_title = search["tracks"]["items"][0]["name"]
            query_artist = search["tracks"]["items"][0]["artists"][0]["name"]
            print(f"SONG NOT ADDED, EXPLICIT:{query_song_title} by {query_artist}")
            track_uri = "REMOVE"
    query_song_title = search["tracks"]["items"][0]["name"]
    query_artist = search["tracks"]["items"][0]["artists"][0]["name"]
    if ask: add = input(f"Add track? {query_song_title} by {query_artist} (Y/N): ")
    else: add = "y"

    if add.lower() == "y": return track_uri
    else: track_uri = "REMOVE"
    return track_uri

def multi_search_song(song_title: str, artist: str, explicit_check:bool, ask:bool, num_query:int, spotify) -> str:
    song_title = song_title.replace(' ', '%20')
    artist = artist.replace(' ', '%20')
    query = 'track%20'+song_title+'%20artist%20'+artist
    search = spotify.search(q=query, limit=num_query, type='track')

    
    for i in range(num_query):
        query_song_title = search["tracks"]["items"][i]["name"]
        query_artist = search["tracks"]["items"][i]["artists"][0]["name"]
        explicit_flag = search["tracks"]["items"][i]["explicit"]
        if explicit_flag: print(f"EXPLICIT---Track {i+1}: {query_song_title} by {query_artist}")
        else: print(f"CLEAN------Track {i+1}: {query_song_title} by {query_artist}")
    if num_query > 1:
        user_select = int(input(f"Select a track 1-{num_query}: "))
        user_select -= 1
    else: 
        user_select = 0
    query_song_title = search["tracks"]["items"][user_select]["name"]
    query_artist = search["tracks"]["items"][user_select]["artists"][0]["name"]
    print(f"Adding: {query_song_title} by {query_artist}")
    track_uri = search["tracks"]["items"][user_select]["uri"]

    if explicit_check and search["tracks"]["items"][0]["explicit"] == True:
        print(f"SONG NOT ADDED, EXPLICIT:{query_song_title} by {query_artist}")
        track_uri = "REMOVE"
        return track_uri
    
    if ask: add = input(f"Confirm adding? {query_song_title} by {query_artist} (Y/N): ")
    else: add = "y"

    if add.lower() == "y": return track_uri
    else: track_uri = "REMOVE"
    return track_uri


# def add_to_playlist(song_ids: list, playlist_id: str, spotify):
#     spotify.user_playlist_add_tracks(user=user_uri, playlist_id=playlist_id, tracks=song_ids)


def search_playlist(playlist_id: str, spotify):  # song_ids: list,
    # TODO What if they are more than 100 songs?
    song_uris = []
    playlist = spotify.user_playlist_tracks(playlist_id=playlist_id)
    playlist.pop(next(iter(playlist)))
    for track in playlist.items():
        if isinstance(track[1], list):
            for song in track[1]:
                song_uris.append(song["track"]["uri"])
    return song_uris

# def delete_playlist_songs(spotify):
#     spotify.user_playlist_remove_specific_occurrences_of_tracks(user=user_uri, playlist_id=playlist_id, tracks=song_ids)

def parse_songs(file_name: str) -> list:
    raw_songs = []
    songs = []
    file = open(file_name, "r")
    for line in file:
        if not line.isspace():
            length = len(line)
            raw_songs.append(line[:length-1])
    file.close()
    raw_songs = raw_songs[2:]
    for song in raw_songs:
        split_song = song.split(", ")
        title = split_song[0]
        artist = split_song[1]
        songs.append((title, artist))
    return songs


def main():
    spotify = user_auth()
    user_uri = 'spotify:user:129893381'

    playlist_id = 'https://open.spotify.com/playlist/2aQGNM7ARYNvyTWnHFzAr1'
    # playlist_id = 'https://open.spotify.com/playlist/17zxFSXnwKpaG3ImXPPodk'
    playlist = spotify.playlist(playlist_id)
    playlist_uri = playlist["uri"]

    curr_songs = search_playlist(playlist_id=playlist_uri, spotify=spotify)

    print(curr_songs)

    # for song in new_song:
    #     if song in curr_songs:
    #         new_song.remove(song)

    # print(new_song)

    songs = parse_songs("class_playlist.txt")
    for song in songs:
        song_id  = multi_search_song(song[0], song[1],explicit_check=True, ask=False,num_query=1, spotify=spotify)
        print(song_id)
    

    # UNCOMMENT LATER
    # song_ids = []
    # songs = parse_songs("class_playlist.txt")
    # print(songs)
    # for song in songs:
    #     song_id  = search_song(song[0], song[1],explicit=False, ask=False, spotify=spotify)
    #     if song_id != "REMOVE": song_ids.append(song_id)
    # print("------MEOW-----------------------------------------")
    # print(song_ids)
    # print("----------------MONNONON-------------------------------")
    # curr_songs = search_playlist(playlist_id=playlist_uri, spotify=spotify)
    # for song_id in song_ids:
    #     if song_id in curr_songs:
    #         song_ids.remove(song_id)
    # print("----------------RERSDS-------------------------------")
    # print(song_ids)
    # spotify.user_playlist_remove_all_occurrences_of_tracks(user=user_uri, playlist_id=playlist_id, tracks=song_ids)
    # spotify.user_playlist_add_tracks(
    #     user=user_uri, playlist_id=playlist_id, tracks=song_ids)
    
    # ^^^^^^^^^^



    # playlist_id = 'https://open.spotify.com/playlist/1Ir68GCjAflF4M8sVSN9Of'

    # playlist = spotify.playlist(playlist_id)

    # playlist_uri = playlist["uri"]

    # track_spotify_url = search["tracks"]["items"][0]["external_urls"]["spotify"]
    # track_uri = search["tracks"]["items"][0]["uri"]

    # user = spotify.user("129893381")
    # user_id = "129893381"
    # user_uri = user["uri"]

    # playlist_uri = 'spotify:playlist:1Ir68GCjAflF4M8sVSN9Of'
    # # track_uris = ['spotify:track:1xicvSO4CJ2ymqYgpk7DFh',
    # #               'spotify:track:1xicvSO4CJ2ymqYgpk7DFh']
    # # track_uri = 'spotify:track:1xicvSO4CJ2ymqYgpk7DFh'
    # # print(user_uri)
    # # print(track_spotify_url)
    # # print(test2)

    # print(user_uri)
    # print(playlist_uri)
    # print(track_uri)

    # spotify.add_to_queue(track_uri)

    # # sp.user_playlist_add_tracks(
    # #     user=user_uri, playlist_id=playlist_uri, tracks=track_uri, position=None)
    # # print(playlist)
    # # results = sp.current_user_saved_tracks()
    # # for idx, item in enumerate(results['items']):
    # #     track = item['track']
    # #     print(idx, track['artists'][0]['name'], " - ", track['name'])


if __name__ == "__main__":
    main()
