# -*- coding: utf-8 -*-
import logging
import youtube_dl
from random import shuffle
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session, audio, current_stream
import subprocess
from bs4 import BeautifulSoup
import urllib
import urllib2
import json
#   GOOLGE / YOUTUBE IMPORTS
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

YOUTUBE_PLAYLIST_ID = "PLAYLIST_ID_FOR_YOUR_YOUTUBE_PLAYLIST"
DEVELOPER_KEY = "API_KEY_FROM_GOOGLE_CONSOLE"   # make sure to enable YouTube Api in Developer Console
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger("flask_ask").setLevel(logging.DEBUG)

def match_class(target):
    def do_match(tag):
        classes = tag.get('class', [])
        return all(c in classes for c in target)
    return do_match


@ask.launch
def welcome():
    welcome_msg = render_template('welcome')
    return question(welcome_msg)


###################################################################
#                                                                 #  
#   "Alexa, öffne YouTube und starte Playlist"                    #
#                                                                 #
#   Spielt die hinterlegte Playlist ab                            #
#                                                                 # 
###################################################################   

@ask.intent("PlaylistIntent")
def play_playlist():
    audio().stop()
    statement(render_template('playlist'))

    songs = fetch_all_youtube_videos(YOUTUBE_PLAYLIST_ID)
    res = []
    for song in songs['items']:
        res.append([song['snippet']['title'], "https://www.youtube.com/?v="+song['snippet']['resourceId']['videoId'].encode('utf-8')])

    #   Mark playlist active, and pop first song
    shuffle(res)
    res.insert(0, [1])
    with open('playlist.json', 'w') as file:
        file.write(json.dumps(res)) # use `json.loads` to do the reverse
    return play_song(str(res[res[0][0]][1]))


###################################################################
#                                                                 #  
#   "Alexa, öffne YouTube und spiele Adele - Someone like you"    #
#                                                                 #
#   Spielt sofort das erste Resultat ab                           #
#                                                                 # 
###################################################################   

@ask.intent("SearchImmediatelyIntent", convert={'lied': str})
def search_immediately_term(lied):
    audio().stop()
    term = lied.replace("for", "")
    term = term.replace("search", "")
    term = term.strip()

    s = { 'search_query':term.encode('utf-8') }
    raw = urllib2.urlopen('https://www.youtube.com/results?'+urllib.urlencode(s))
    html = BeautifulSoup(raw, "html.parser")

    videos = html.findAll(match_class(["yt-lockup-title"]))

    res = []

    for video in videos:
        link = video.findAll('a')[0]
        res.append([link.text, link['href']])

    return play_song('https://www.youtube.com'+str(res[0][1]))




#########################################################################
#                                                                       #
#   "Alexa, öffne YouTube und suche nach Adele - Someone like you"      #
#                                                                       #
#   Gibt die ersten 3 Resultate zur Auswahl                             #
#                                                                       #
#########################################################################

@ask.intent("SearchIntent", convert={'term': str})
def search_term(term):
    audio().stop()
    term = term.replace("for", "")
    term = term.replace("search", "")
    term = term.strip()

    s = { 'search_query':term.encode('utf-8') }

    url = 'https://www.youtube.com/results?'+urllib.urlencode(s)

    print url 

    raw = urllib2.urlopen(url)
    html = BeautifulSoup(raw, "html.parser")

    videos = html.findAll(match_class(["yt-lockup-title"]))

    audio = []

    for video in videos:
        link = video.findAll('a')[0]
        audio.append([link.text, link['href']])

    audio.pop(0)
    audio.pop(0)

    results = render_template('notfound', term=term)

    if len(audio) >= 3:
        results = render_template('choose', audio1=audio[0][0], audio2=audio[1][0], audio3=audio[2][0])
        session.attributes['term'] = term
        session.attributes['results'] = audio

    return question(results.encode('utf-8'))



###################################################################################
#                                                                                 #
#   (ALEXA) "Sag nummer 1 fuer XY, nummer 2 fuer XZ, oder nummer 3 fuer ZY."      #
#   (USER)  "Nummer 3"                                                            #
#                                                                                 #
#   Auswahlintent                                                                 #
#                                                                                 #
###################################################################################

@ask.intent("SelectionIntent", convert={'selection': int})
def select(selection):
    audio = session.attributes['results']
    term = session.attributes['term']

    if 1 > selection > 3:
        return statement(render_template('again'))
    else:
        selection = selection - 1

    return play_song('https://www.youtube.com'+str(audio[selection][1]))
    

###################################################################################
#                                                                                 #
#   Führe Playlist fort (wenn gewollt), wenn Lied fast zuende                     #
#   Muss hierüber gemacht werden, damit das Lied gequeued wird, bevor man         #
#   den Handle verliert sobald das Lied zuende ist                                #
#                                                                                 #
#   Helper Callback                                                               #
#                                                                                 #
###################################################################################

@ask.on_playback_nearly_finished()
def nearly_finished():
    with open('playlist.json', 'r') as file:
        f = json.loads(file.read())
        response = subprocess.Popen(["youtube-dl", f[f[0][0]+1][1], "-j"], stdout=subprocess.PIPE)
        raw = json.loads(response.stdout.read())
        source = ''
        for format in raw['formats']:
            if format['ext'] == 'mp4':
                source = format['url']
        return audio().enqueue(source)



###################################################################################
#                                                                                 #
#   Setze Liedcounter für Playback hoch, wenn Song wirklich zu Ende               #
#                                                                                 #
#   Helper Callback                                                               #
#                                                                                 #
###################################################################################

@ask.on_playback_finished()
def finished():
    with open('playlist.json', 'r') as file:
        f = json.loads(file.read())
    if len(f) > 0:
        f[0][0] = f[0][0]+1
        with open('playlist.json', 'w') as file:
            file.write(json.dumps(f))
    return None



###################################################################################
#                                                                                 #
#   Wenn Playlist existiert, nächstes Lied spielen                                #
#                                                                                 #
###################################################################################

@ask.intent("NextSongIntent")
def next_song():
    with open('playlist.json', 'r') as file:
        f = json.loads(file.read())
    if len(f) > 0:
        f[0][0] = f[0][0]+1
        with open('playlist.json', 'w') as file:
            file.write(json.dumps(f))
        response = subprocess.Popen(["youtube-dl", f[f[0][0]][1], "-j"], stdout=subprocess.PIPE)
        raw = json.loads(response.stdout.read())
        source = ''
        for format in raw['formats']:
            if format['ext'] == 'mp4':
                source = format['url']
        return audio().play(source)


###################################################################################
#                                                                                 #
#   Spiele Song ab (Helper Function)                                              #
#                                                                                 #
###################################################################################

def play_song(uri):
    response = subprocess.Popen(["youtube-dl", uri, "-j"], stdout=subprocess.PIPE)
    raw = json.loads(response.stdout.read())
    source = ''
    for format in raw['formats']:
        if format['ext'] == 'mp4':
            source = format['url']
    return audio().play(source)


@ask.intent('AMAZON.PauseIntent')
def pause():
    return audio().stop()


@ask.intent('AMAZON.ResumeIntent')
def resume():
    return audio().resume()


@ask.intent('AMAZON.StopIntent')
def stop():
    return audio().clear_queue(stop=True)

#############   GOOGLE / YOUTUBE LOGIN   ####################

def fetch_all_youtube_videos(playlistId):
    youtube = build(YOUTUBE_API_SERVICE_NAME,
                    YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)
    res = youtube.playlistItems().list(
    part="snippet",
    playlistId=playlistId,
    maxResults="50"
    ).execute()

    nextPageToken = res.get('nextPageToken')
    while ('nextPageToken' in res):
        nextPage = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlistId,
        maxResults="50",
        pageToken=nextPageToken
        ).execute()
        res['items'] = res['items'] + nextPage['items']

        if 'nextPageToken' not in nextPage:
            res.pop('nextPageToken', None)
        else:
            nextPageToken = nextPage['nextPageToken']

    return res

if __name__ == '__main__':
    app.run(port=80, debug=True)