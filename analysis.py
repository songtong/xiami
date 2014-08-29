# analysis.py
# coding=utf-8
import os

class Artist:
    def __init__(self):
        self.id = int()
        self.name = str()
        self.songs = []
        
class Song:
    def __init__(self):
        self.name = str()
        self.listened = int()

artists = dict()

def load():
    global artists
    for dirname, dirnames, filenames in os.walk('.'):  # @UnusedVariable
        for file_name in filenames:
            if file_name.startswith('artists_') and file_name.endswith('.txt'):
                fp = open(file_name, 'r')
                for line in fp.readlines():
                    if not line.startswith('\t'):
                        artist = Artist()
                        parts = line.split('\t')
                        artist.id = parts[0]
                        artist.name = parts[1]
                        artists[artist.id] = artist
                    else:
                        song = Song()
                        parts = line.split('\t')
                        song.name = parts[1]
                        song.listened = parts[2].strip()
                        artist.songs.append(song)
        break

load()

for id, artist in artists.items():  # @ReservedAssignment
    for song in artist.songs:
        print '{0}\t{1}\t{2}\t{3}'.format(id, artist.name, song.name, song.listened)
