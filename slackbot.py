import requests
import time
import json
import os
import logging
from slackclient import SlackClient

# future variable to work as emergency shutoff valve if something goes bonkers
shutoffValve = False

# globally-used tokens and objects
spotifyAccessToken = "your spotify access token"
spotifyRefreshToken = "your spotify refresh token"
slackToken = "your slack token"
sc = None


def listenToSlack():
    """listens to each message in the slack group and takes action based
        on the content of specific messages"""
    # sc = SlackClient(slackToken)
    if sc.rtm_connect():
        while not shutoffValve:
            # read a message from slack
            lastMessage = sc.rtm_read()

            # try parsing the message contents
            try:
                messageBody = parseMessage(lastMessage)
            except Exception as e:
                logging.error('had trouble parsing message')
                logging.error(lastMessage)
                logging.error(type(e))
                logging.error(e)

            # ff the message body contains a spotify track...
            if "https://open.spotify.com/track" in messageBody:
                # add the track to the spotify playlist
                try:
                    addedTrackID = addSpotifyTrack(messageBody)
                except Exception as e:
                    logging.error('error adding spotify track')
                    logging.error(messageBody)
                    logging.error(type(e))
                    logging.error(e)

                # get info about the track from spotify
                try:
                    trackDetails = getSpotifyTrackInfo(addedTrackID)
                except Exception as e:
                    logging.error('error retrieving track info')
                    logging.error(addedTrackID)
                    logging.error(type(e))
                    logging.error(e)

                # tell the channel which track was added and bump playlist
                try:
                    sendTrackDetails(sc, trackDetails)
                except Exception as e:
                    logging.error('error sending track details')
                    logging.error(trackDetails)
                    logging.error(type(e))
                    logging.error(e)

            # if someone in the general channel asks to see a meme...
            elif "<@U1WN69MJT>: pepe" in messageBody
              or "<@U1WN69MJT> pepe" in messageBody
              or "<@U1WN69MJT>: Pepe" in messageBody
              or "<@U1WN69MJT> Pepe" in messageBody:
            #   ...try sending a meme
                try:
                    sendPepe()
                except Exception as e:
                    logging.error('error sending pepe')
                    logging.error(type(e))
                    logging.error(e)

            # wait briefly before checking out the next message
            time.sleep(1)

def parseMessage(message):
    messageDict = None

    # get contents of message, of available
    if len(message) > 0: messageDict = message[0]
    # grab the value in the text attribute of the message dictionary
    if messageDict is not None and 'text' in messageDict:
        return messageDict["text"]

    return None

def sendPepe():
    import random

    # grab a random file from the current directory (which should be full of pics - see main)
    imgName = random.choice(os.listdir(os.getcwd()))
    # read the image as a binary blob
    f = open(imgName, 'rb')
    # upload the file to slack
    print(sc.api_call('files.upload', channels=["your slack channel"], filename="Pepe for Normies Upload", files={"file":f}))

def getSpotifyTrackInfo(trackID):
    # make call to spotify api to get track info
    header = {"Authorization": "Bearer " + spotifyAccessToken}
    infoUrl = "https://api.spotify.com/v1/tracks/" + trackID
    infoResponse = requests.get(infoUrl, headers=header)


    if infoResponse.status_code is not 404:
        # parse JSON response from spotify, grabbing the song name and name of first artist
        jsonDict = json.loads(infoResponse.text)
        songName = jsonDict["name"]
        artistName = jsonDict["artists"][0]["name"]
        return songName + " by " + artistName
    # print(infoResponse)
    # print(addResponse.text)

def addSpotifyTrack(message):
    # determine which part of the slack message contains the spotify link
    urlStartIndex = message.find("https://open.spotify.com/track")
    try:
        spaceIndex = message.index(' ', urlStartIndex)
    except Exception as e:
        spaceIndex = len(message)

    # clean up spotify track
    trackURL = message[urlStartIndex:spaceIndex]
    trackURL = trackURL.rstrip('>')
    spUriStartIndex = trackURL.rfind("/")
    # grab the numeric spotify track ID
    trackID = trackURL[spUriStartIndex + 1:]

    # grab a new spotify access token since they expire very quickly
    refreshAccessToken()

    header = {"Authorization": "Bearer " + spotifyAccessToken}
    query = {"uris": "spotify:track:" + trackID}
    # post the new track to the spotify playlist
    addResponse = requests.post("https://api.spotify.com/v1/users/your_spotify_username/playlists/your_spotify_playlist_id/tracks",
                                params=query,
                                headers=header)
    # return the track ID to get the track info
    return trackID

def sendTrackDetails(client, trackString):
    # format message to be sent to the channel
    output = trackString + " has been added to the playlist. Check it out here: https://open.spotify.com/user/your_spotify_username/playlist/your_spotify_playlist_id"

    # find the channel and send the message
    channel = client.server.channels.find("your slack channel")

    if channel is not None:
            channel.send_message(output)


def refreshAccessToken():
    # construct token request header
    global spotifyAccessToken
    payloadr = {"refresh_token": spotifyRefreshToken,
                "grant_type":"refresh_token",
                "client_id": "your spotify client ID",
                "client_secret":"your spotify client secret"}

    # post the access token request
    refr = requests.post("https://accounts.spotify.com/api/token", data=payloadr)
    # return the token
    spotifyAccessToken = json.loads(refr.text)["access_token"]

if __name__ == '__main__':
    # set up logging for exceptions
    logging.basicConfig(filename='runtime.log',level=logging.DEBUG)
    # change directory to folder where images to be posted resides
    os.chdir("Pepe")
    # open up the slack connection
    sc = SlackClient(slackToken)
    # start listening to slack traffic
    listenToSlack()
