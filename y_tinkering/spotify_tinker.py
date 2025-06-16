# REFERENCE: https://medium.com/analytics-vidhya/steal-songs-from-your-friends-on-spotify-using-python-3c3b654b4375
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
# from spotipy.oauth2 import SpotifyOAuth
import SetupModule
import math
from collections import Counter

cid = 'your cid'
secret = 'your secret'
username = 'username of user'
friendUsernames = [#add in friend usernames in this format
                   'username' + , #]
playlistLength = 100
maxMatchFactor = len(friendUsernames)
numFriends = len(friendUsernames)
compilerId = 'spotify:playlist:identifier for playlist to fill'
setupTool = SetupModule.Setup(cid,secret, username)
spotify = setupTool.createAndReturnAuthenticatedSpotifyInstance()
# find the most tracks that each individual liked the most
def findIndividualFavorites():
    allFavorites = []
    personalShare = math.ceil((0.5 * playlistLength)/numFriends)
    for i in range(len(friendTrackData)):
        curUser = friendTrackData[i]
        tracks = curUser['userTracks']
        occurence_count = Counter(tracks)
        mostPopular = occurence_count.most_common(personalShare)
        temp = dict(mostPopular)
        allFavorites += temp.keys()
    return allFavorites
# add track operation can only support a list of max size 100 so if we have more track than that
# break total tracks into a bunch of size 99 chunks and add those iteratively
def addTracksToPlaylist(tracksToAdd):
    if len(tracksToAdd) > 99:
        generator = chunks(tracksToAdd,99)
        for value in generator:
            spotify.user_playlist_add_tracks(username, compilerId,
            value, position=None)
    else:
        spotify.user_playlist_add_tracks(username, compilerId,
         tracksToAdd, position=None)
# find songs that everyone likes
def findPopularAmongAll(matchFactors):
    popularAmongAll = []
    while( len(popularAmongAll) != math.ceil((0.5*playlistLength))):
        for p in range( maxMatchFactor-1,0,-1):
            if  len(matchFactors[p]) != 0 :
                popularAmongAll.append(matchFactors[p].pop())
                break
    return popularAmongAll
def sortByMatchFactor(totalTracksClean):
    matchFactorCollection = {k: [] for k in range(maxMatchFactor)}

    for x in range(len(totalTracksClean)):
        curTrack = totalTracksClean[x]
        trackMatchFactor = getMatchFactor(curTrack)
        for i in range(maxMatchFactor,0,-1):
            if trackMatchFactor > i:
                matchFactorCollection[i].append(curTrack)
                break
    return matchFactorCollection
# match factor is the number of friend's who had this track in their # playlist
def getMatchFactor(the_track):
    matchFactor = 0
    for i in range(len(friendTrackData)):
        curUser = friendTrackData[i]
        tracks = curUser['userTracks']
        if tracks.count(the_track) > 0:
            matchFactor += 1
    return matchFactor
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
playlists = spotify.user_playlists(username)
totalTracks, friendTrackData =  setupTool.initializeData(friendUsernames, spotify)
totalTracksClean = list(dict.fromkeys(totalTracks))
matchFactors = sortByMatchFactor(totalTracksClean)
popularAmongAll = findPopularAmongAll(matchFactors)
individualFavs = findIndividualFavorites()
tracksOfPlaylist = popularAmongAll + individualFavs
addTracksToPlaylist(tracksOfPlaylist)
