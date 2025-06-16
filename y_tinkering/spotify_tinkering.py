# REFERENCE: https://medium.com/analytics-vidhya/steal-songs-from-your-friends-on-spotify-using-python-3c3b654b4375
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
# from spotipy.oauth2 import SpotifyOAuth


class Setup(object):
    cid = ''
    secret = ''
    primaryUsername = ''
    scope = "playlist-modify-public"

    def __init__(self, cid, secret, primaryUsername):
        Setup.cid = cid
        Setup.secret = secret
        Setup.primaryUsername = primaryUsername


    def createAndReturnAuthenticatedSpotifyInstance(self):
        token = util.prompt_for_user_token(
            Setup.primaryUsername,
            Setup.scope,
            client_id=Setup.cid,
            client_secret=Setup.secret,
            redirect_uri='http://localhost/'
        )
        spotify = spotipy.Spotify(auth=token)
        return spotify


    def initializeData(self, friendUsernames, spotify):
        totalTracks = []
        friendTrackData = []
        for i in range(len(friendUsernames)):
            username = friendUsernames[i]
            playlists = spotify.user_playlists(username)
            userTracks = []
            while playlists:
                for i, playlist in enumerate(playlists['items']):
                    playlistTracks =
                    spotify.playlist_tracks(playlist['uri'])
                    trackItems = playlistTracks['items']
                    for k in range(len(trackItems)):
                        trackItem = trackItems[k]
                        track = trackItem['track']
                        userTracks.append(track['uri'])
                        totalTracks.append(track['uri'])
                if playlists['next']:
                    playlists = spotify.next(playlists)
                else:
                    playlists = None
            dictOfData = {"user":username, "userTracks":userTracks}
            friendTrackData.append(dictOfData)
        return totalTracks, friendTrackData
