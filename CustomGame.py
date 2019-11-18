# Game screen of Custom mode

import pygame as pg
import pyaudio as pa
import wave
import numpy as np
import random
import threading

import tkinter as tk
from tkinter import filedialog # will need tkinter to prompt user for file

from Buttons import *
from Sprites import *

from NormalGame import *

from BeatDetection import *

# CITATION: Threading function decorator from Stack Overflow
# https://stackoverflow.com/questions/19846332/python-threading-inside-a-class
def threaded(fn):
    # will take a function and make it threaded
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper

class CustomGame(NormalGame):

    def __init__(self, width, height, hard=False):
        # initializes all variables needed for the game
        super().__init__(width, height, hard)
        self.background = (0,0,0)
        self.isBeat = False
        self.frequency = 0
        self.audioPath = ""
        self.BeatDetection = BeatDetection()

    def getHighScores(self):
        # get high scores and songs out of text files stored on computer
        scores = self.readFile('data/HighScoresCustom.txt').splitlines()
        songs = self.readFile('data/HighSongsCustom.txt').splitlines()
        highScores = dict()
        if len(scores) == 0:
            highScores[0] = 'No data'
        else:
            for i in range(len(scores)):
                score = scores[i]
                song = songs[i]
                highScores[float(score)] = song
        return highScores

    def getAudioFile(self):
        # prompts user to input a .wav file and keeps prompting if user cancels

        root = tk.Tk()
        root.withdraw()

        path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])

        if path == "":
            print("No file inputted.")
            path = self.getAudioFile()

        self.path = path
        return path

    @threaded
    def playMusic(self):
        # plays .wav file and will restart when done playing
        # will also check whether current chunk is a beat and get dominant frequency

        CHUNK = 1024

        audio = wave.open(self.audioPath, 'rb')
        p = pa.PyAudio()

        self.isPlayingGame = True

        # open stream based on the wave file
        stream = p.open(format =
                        p.get_format_from_width(audio.getsampwidth()),
                        channels = audio.getnchannels(),
                        rate = audio.getframerate(),
                        output = True)

        data = audio.readframes(CHUNK)

        self.donePlayingMusic = False

        while self.isPlayingMusic and len(data) > 0:
            # writing to the stream plays the sound
            stream.write(data)
            isBeat, frequency = self.BeatDetection.detectBeat(data)
            if isBeat:
                self.isBeat = True
                self.frequency = frequency
            else:
                self.isBeat = False
            data = audio.readframes(CHUNK)

        stream.stop_stream()
        stream.close()
        p.terminate()

        self.donePlayingMusic = True

    def getRGBValue(self, frequency):
        # based on frequency, generate a background color
        # inspired from Google's RGB color picker
        # https://www.google.com/search?q=RGB+Color+Picker
        # (input (128,0,0) and move the slider)
        if frequency >= 15005:
            frequency -= 14985
        elif frequency >= 10010:
            frequency -= 9990
        elif frequency >= 5015:
            frequency -= 4995
        if frequency < 20 or frequency >= 5015:
            r = 128
            g = 0
            b = 0
        elif 20 <= frequency < 852.5:
            r = 128
            g = int((128/832.5)*(frequency - 20))
            b = 0
        elif 852.5 <= frequency < 1685:
            r = int((-128/832.5)*(frequency - 1685))
            g = 128
            b = 0
        elif 1685 <= frequency < 2517.5:
            r = 0
            g = 128
            b = int((128/832.5)*(frequency - 1685))
        elif 2517.5 <= frequency < 3350:
            r = 0
            g = int((-128/832.5)*(frequency - 3350))
            b = 128
        elif 3350 <= frequency < 4182.5:
            r = int((128/832.5)*(frequency - 3350))
            g = 0
            b = 128
        elif 4182.5 <= frequency < 5015:
            r = 128
            g = 0
            b = int((-128/832.5)*(frequency - 5015))
        return (r,g,b)

    def storeHighScores(self):
        # overwrites text files with updated high scores and songs
        while len(self.highScores) > 5:
            smallest = min(self.highScores)
            del self.highScores[smallest]
        scores = [ ]
        songs = [ ]
        for item in self.highScores:
            scores.append(str(item))
            songs.append(self.highScores[item])
        scoresText = '\n'.join(scores)
        songsText = '\n'.join(songs)
        self.writeFile('data/HighScoresCustom.txt', scoresText)
        self.writeFile('data/HighSongsCustom.txt', songsText)

    def timerFired(self, dt):
        # scales obstacles, moves arrow, changes background color
        # if there is beat, and replays music when done playing
        if self.isPlayingGame:
            self.timeElapsed += dt
            self.timeGap += dt
            self.scaleObstacles()
            if self.isBeat and self.timeGap > self.waitTime:
                self.timeGap = 0
                self.generateObstacle()
                self.background = self.getRGBValue(self.frequency)
            if self.isMovingLeft:
                self.moveArrow('left')
            elif self.isMovingRight:
                self.moveArrow('right')
            if self.isPlayingMusic and self.donePlayingMusic:
                self.playMusic()
                self.donePlayingMusic = False

    def redrawAll(self, screen):
        # draw game screen
        screen.fill(self.background)
        super().redrawAll(screen)