####################################################
#             15-112 F18 Term Project              #
#     Super Py-gon (inspired by Super Hexagon)     #
#          Made by Andrew Sheng / asheng2          #
####################################################

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

from MainSplash import *
from NormalSplash import *
from NormalLeader import *
from CustomSplash import *
from CustomLeader import *
from VersusSplash import *
from OnlineSplash import *

from NormalGame import *
from CustomGame import *
from VersusGame import *
from OnlineGame import *

from BeatDetection import *

import time

# CITATION: Sockets starter code from Kyle
# https://kdchin.gitbooks.io/sockets-module-manual/
# Modified for use with Pygame and to still allow users to
# play the game locally if unable to connect to server

import socket
import threading
from queue import Queue

HOST = "127.0.0.1" # put host IP address here if playing online
PORT = 50005

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    server.connect((HOST,PORT))
    print("Connected to server")
    connected = True
except:
    print("Unable to connect to server")
    connected = False

def handleServerMsg(server, serverMsg):
    server.setblocking(1)
    msg = ""
    command = ""
    while True:
        msg += server.recv(10).decode("UTF-8")
        command = msg.split("\n")
        while (len(command) > 1):
            readyMsg = command[0]
            msg = "\n".join(command[1:])
            serverMsg.put(readyMsg)
            command = msg.split("\n")

# Game code starts here

# CITATION: Pygame starter code from Lukas Peraza
# https://github.com/LBPeraza/Pygame-Asteroids/blob/master/pygamegame.py
# Modified to add certain mechanics and for use with sockets

class Game():

    def init(self):
        self.player = None
        t1 = time.time()
        self.mode = 'MainSplash'
        self.MainSplash = MainSplash(self.width, self.height)
        self.NormalSplash = NormalSplash(self.width, self.height)
        self.NormalLeader = NormalLeader(self.width, self.height)
        self.CustomSplash = CustomSplash(self.width, self.height)
        self.CustomLeader = CustomLeader(self.width, self.height)
        self.VersusSplash = VersusSplash(self.width, self.height)
        self.OnlineSplash = OnlineSplash(self.width, self.height, self.server)
        self.NormalGame = NormalGame(self.width, self.height)
        self.CustomGame = CustomGame(self.width, self.height)
        self.VersusGame = VersusGame(self.width, self.height)
        self.OnlineGame = OnlineGame(self.width, self.height, self.server)
        # force aliasing between classes to avoid passing
        # high scores between them everytime it gets updated
        self.NormalSplash.highScores = self.NormalGame.highScores
        self.NormalLeader.highScores = self.NormalGame.highScores
        self.CustomSplash.highScores = self.CustomGame.highScores
        self.CustomLeader.highScores = self.CustomGame.highScores
        t2 = time.time()
        print('Load time: %0.3f sec' %(t2-t1))

    #### START GAME HELPER FUNCTIONS ####

    def startNormalGame(self):
        self.mode = 'NormalGame'
        self.NormalGame.isPlayingGame = True
        self.NormalGame.isPlayingMusic = True
        self.NormalGame.playMusic()

    def startCustomGame(self):
        self.mode = 'CustomGame'
        self.CustomGame.isPlayingMusic = True
        self.CustomGame.audioPath = self.CustomGame.getAudioFile()
        self.CustomGame.playMusic()

    def startVersusGame(self):
        self.mode = 'VersusGame'
        self.VersusGame.isPlayingGame = True
        self.VersusGame.isPlayingMusic = True
        self.VersusGame.playMusic()

    def startOnlineGame(self):
        if not self.OnlineGame.isPlayingGame:
            # make sure the game doesn't start twice if both players press start
            self.mode = 'OnlineGame'
            self.OnlineGame.isPlayingGame = True
            self.OnlineGame.isPlayingMusic = True
            self.OnlineGame.playMusic()

    #### QUIT GAME HELPER FUNCTIONS ####

    def quitNormalGame(self):
        self.mode = 'NormalSplash'
        self.NormalGame.__init__(self.width, self.height)
        self.NormalGame.highScores = self.NormalSplash.highScores

    def quitCustomGame(self):
        self.mode = 'CustomSplash'
        self.CustomGame.__init__(self.width, self.height)
        self.CustomGame.highScores = self.CustomSplash.highScores

    def quitVersusGame(self):
        self.mode = 'VersusSplash'
        self.VersusGame.__init__(self.width, self.height)

    def quitOnlineGame(self):
        self.mode = 'OnlineSplash'
        player = self.OnlineGame.player
        otherConnected = self.OnlineGame.otherConnected
        self.OnlineGame.__init__(self.width, self.height, self.server)
        self.OnlineGame.player = player
        self.OnlineGame.otherConnected = otherConnected

    #### RESET GAME HELPER FUNCTIONS ####

    def resetNormalGame(self):
        self.NormalGame.__init__(self.width, self.height)
        self.NormalGame.highScores = self.NormalSplash.highScores
        self.NormalGame.isPlayingGame = True
        self.NormalGame.isPlayingMusic = True
        self.NormalGame.playMusic()

    def resetCustomGame(self):
        audioPath = self.CustomGame.audioPath
        self.CustomGame.__init__(self.width, self.height)
        self.CustomGame.audioPath = audioPath
        self.CustomGame.highScores = self.CustomSplash.highScores
        self.CustomGame.isPlayingGame = True
        self.CustomGame.isPlayingMusic = True
        self.CustomGame.playMusic()

    def resetVersusGame(self):
        self.VersusGame.__init__(self.width, self.height)
        self.VersusGame.isPlayingGame = True
        self.VersusGame.isPlayingMusic = True
        self.VersusGame.playMusic()

    def resetOnlineGame(self):
        if not self.OnlineGame.isPlayingGame:
            # make sure the game doesn't restart twice if both players press restart
            player = self.OnlineGame.player
            otherConnected = self.OnlineGame.otherConnected
            self.OnlineGame.__init__(self.width, self.height, self.server)
            self.OnlineGame.player = player
            self.OnlineGame.otherConnected = otherConnected
            self.OnlineGame.isPlayingGame = True
            self.OnlineGame.isPlayingMusic = True
            self.OnlineGame.playMusic()

    # MOUSE PRESSED HELPER FUNCTIONS ####

    def MainSplashMousePressed(self, x, y):
        self.mode = 'NormalSplash'

    def NormalSplashMousePressed(self, x, y):
        if self.NormalSplash.backButton.rect.collidepoint(x, y):
            self.mode = 'MainSplash'
        elif self.NormalSplash.leftButton.rect.collidepoint(x, y):
            self.mode = 'OnlineSplash'
        elif self.NormalSplash.rightButton.rect.collidepoint(x, y):
            self.mode = 'CustomSplash'
        elif self.NormalSplash.leaderButton.rect.collidepoint(x, y):
            self.mode = 'NormalLeader'
        else:
            self.startNormalGame()

    def NormalLeaderMousePressed(self, x, y):
        if self.NormalLeader.backButton.rect.collidepoint(x, y):
            self.mode = 'NormalSplash'

    def CustomSplashMousePressed(self, x, y):
        if self.CustomSplash.backButton.rect.collidepoint(x, y):
            self.mode = 'MainSplash'
        elif self.CustomSplash.leftButton.rect.collidepoint(x, y):
            self.mode = 'NormalSplash'
        elif self.CustomSplash.rightButton.rect.collidepoint(x, y):
            self.mode = 'VersusSplash'
        elif self.CustomSplash.leaderButton.rect.collidepoint(x, y):
            self.mode = 'CustomLeader'
        else:
            self.startCustomGame()

    def CustomLeaderMousePressed(self, x, y):
        if self.NormalLeader.backButton.rect.collidepoint(x, y):
            self.mode = 'CustomSplash'

    def VersusSplashMousePressed(self, x, y):
        if self.VersusSplash.backButton.rect.collidepoint(x, y):
            self.mode = 'MainSplash'
        elif self.VersusSplash.leftButton.rect.collidepoint(x, y):
            self.mode = 'CustomSplash'
        elif self.VersusSplash.rightButton.rect.collidepoint(x, y):
            self.mode = 'OnlineSplash'
        else:
            self.startVersusGame()

    def OnlineSplashMousePressed(self, x, y):
        if self.OnlineSplash.backButton.rect.collidepoint(x, y):
            self.mode = 'MainSplash'
        elif self.OnlineSplash.leftButton.rect.collidepoint(x, y):
            self.mode = 'VersusSplash'
        elif self.OnlineSplash.rightButton.rect.collidepoint(x, y):
            self.mode = 'NormalSplash'
        elif self.OnlineGame.otherConnected:
            msg = 'start online\n'
            self.server.send(msg.encode())
            self.startOnlineGame()

    def NormalGameMousePressed(self, x, y):
        if self.NormalGame.isPlayingGame == False and \
            self.NormalGame.backButton.rect.collidepoint(x, y):
            self.quitNormalGame()
        elif self.NormalGame.isPlayingGame == False:
            self.resetNormalGame()
        else:
            self.NormalGame.mousePressed(x, y)

    def CustomGameMousePressed(self, x, y):
        if self.CustomGame.isPlayingGame == False and \
            self.CustomGame.backButton.rect.collidepoint(x, y):
            self.quitCustomGame()
        elif self.CustomGame.isPlayingGame == False:
            self.resetCustomGame()
        else:
            self.CustomGame.mousePressed(x, y)

    def VersusGameMousePressed(self, x, y):
        if self.VersusGame.isPlayingGame == False and \
            self.VersusGame.backButton.rect.collidepoint(x, y):
            self.quitVersusGame()
        elif self.VersusGame.isPlayingGame == False:
            self.resetVersusGame()
        # there is no mousePressed for VersusGame

    def OnlineGameMousePressed(self, x, y):
        if self.OnlineGame.isPlayingGame == False and \
            self.OnlineGame.backButton.rect.collidepoint(x, y):
            msg = 'quit online\n'
            self.server.send(msg.encode())
            self.quitOnlineGame()
        elif self.OnlineGame.isPlayingGame == False:
            msg = 'reset online\n'
            self.server.send(msg.encode())
            self.resetOnlineGame()
        # there is no mousePressed for OnlineGame

    def mousePressed(self, x, y):
        if self.mode == 'MainSplash':
            self.MainSplashMousePressed(x, y)
        elif self.mode == 'NormalSplash':
            self.NormalSplashMousePressed(x, y)
        elif self.mode == 'NormalLeader':
            self.NormalLeaderMousePressed(x, y)
        elif self.mode == 'CustomSplash':
            self.CustomSplashMousePressed(x, y)
        elif self.mode == 'CustomLeader':
            self.CustomLeaderMousePressed(x, y)
        elif self.mode == 'VersusSplash':
            self.VersusSplashMousePressed(x, y)
        elif self.mode == 'OnlineSplash':
            self.OnlineSplashMousePressed(x, y)
        elif self.mode == 'NormalGame':
            self.NormalGameMousePressed(x, y)
        elif self.mode == 'CustomGame':
            self.CustomGameMousePressed(x, y)
        elif self.mode == 'VersusGame':
            self.VersusGameMousePressed(x, y)
        elif self.mode == 'OnlineGame':
            self.OnlineGameMousePressed(x, y)

    def mouseReleased(self, x, y):
        if self.mode == 'NormalGame':
            self.NormalGame.mouseReleased(x, y)
        elif self.mode == 'CustomGame':
            self.CustomGame.mouseReleased(x, y)

    def mouseMotion(self, x, y):
        pass

    def mouseDrag(self, x, y):
        pass

    #### KEY PRESSED HELPER FUNCTIONS ####

    def MainSplashKeyPressed(self, keyCode, modifier):
        if keyCode == pg.K_RETURN or keyCode == pg.K_KP_ENTER or \
            keyCode == pg.K_SPACE:
            self.mode = 'NormalSplash'

    def NormalSplashKeyPressed(self, keyCode, modifier):
        if keyCode == pg.K_LEFT:
            self.mode = 'OnlineSplash'
        elif keyCode == pg.K_RIGHT:
            self.mode = 'CustomSplash'
        elif keyCode == pg.K_RETURN or keyCode == pg.K_KP_ENTER or \
            keyCode == pg.K_SPACE:
            self.startNormalGame()
        elif keyCode == pg.K_q or keyCode == pg.K_ESCAPE:
            self.mode = 'MainSplash'
        elif keyCode == pg.K_l:
            self.mode = 'NormalLeader'

    def NormalLeaderKeyPressed(self, keyCode, modifier):
        if keyCode == pg.K_q or keyCode == pg.K_ESCAPE:
            self.mode = 'NormalSplash'

    def CustomSplashKeyPressed(self, keyCode, modifier):
        if keyCode == pg.K_LEFT:
            self.mode = 'NormalSplash'
        elif keyCode == pg.K_RIGHT:
            self.mode = 'VersusSplash'
        elif keyCode == pg.K_RETURN or keyCode == pg.K_KP_ENTER or \
            keyCode == pg.K_SPACE:
            self.startCustomGame()
        elif keyCode == pg.K_q or keyCode == pg.K_ESCAPE:
            self.mode = 'MainSplash'
        elif keyCode == pg.K_l:
            self.mode = 'CustomLeader'

    def CustomLeaderKeyPressed(self, keyCode, modifier):
        if keyCode == pg.K_q or keyCode == pg.K_ESCAPE:
            self.mode = 'CustomSplash'

    def VersusSplashKeyPressed(self, keyCode, modifier):
        if keyCode == pg.K_LEFT:
            self.mode = 'CustomSplash'
        elif keyCode == pg.K_RIGHT:
            self.mode = 'OnlineSplash'
        elif keyCode == pg.K_RETURN or keyCode == pg.K_KP_ENTER or \
            keyCode == pg.K_SPACE:
            self.startVersusGame()
        elif keyCode == pg.K_q or keyCode == pg.K_ESCAPE:
            self.mode = 'MainSplash'

    def OnlineSplashKeyPressed(self, keyCode, modifier):
        if keyCode == pg.K_LEFT:
            self.mode = 'VersusSplash'
        elif keyCode == pg.K_RIGHT:
            self.mode = 'NormalSplash'
        elif (keyCode == pg.K_RETURN or keyCode == pg.K_KP_ENTER or \
            keyCode == pg.K_SPACE) and self.OnlineGame.otherConnected:
            msg = 'start online\n'
            self.server.send(msg.encode())
            self.startOnlineGame()
        elif keyCode == pg.K_q or keyCode == pg.K_ESCAPE:
            self.mode = 'MainSplash'

    def NormalGameKeyPressed(self, keyCode, modifier):
        if self.NormalGame.isPlayingGame == False and \
            (keyCode == pg.K_q or keyCode == pg.K_ESCAPE):
            self.quitNormalGame()
        elif self.NormalGame.isPlayingGame == False and keyCode == pg.K_r:
            self.resetNormalGame()
        else:
            self.NormalGame.keyPressed(keyCode, modifier)

    def CustomGameKeyPressed(self, keyCode, modifier):
        if self.CustomGame.isPlayingGame == False and \
            (keyCode == pg.K_q or keyCode == pg.K_ESCAPE):
            self.quitCustomGame()
        elif self.CustomGame.isPlayingGame == False and keyCode == pg.K_r:
            self.resetCustomGame()
        else:
            self.CustomGame.keyPressed(keyCode, modifier)

    def VersusGameKeyPressed(self, keyCode, modifier):
        if self.VersusGame.isPlayingGame == False and \
            (keyCode == pg.K_q or keyCode == pg.K_ESCAPE):
            self.quitVersusGame()
        elif self.VersusGame.isPlayingGame == False and keyCode == pg.K_r:
            self.resetVersusGame()
        else:
            self.VersusGame.keyPressed(keyCode, modifier)

    def OnlineGameKeyPressed(self, keyCode, modifier):
        if self.OnlineGame.isPlayingGame == False and \
            (keyCode == pg.K_q or keyCode == pg.K_ESCAPE):
            msg = 'quit online\n'
            self.server.send(msg.encode())
            self.quitOnlineGame()
        elif self.OnlineGame.isPlayingGame == False and keyCode == pg.K_r:
            msg = 'reset online\n'
            self.server.send(msg.encode())
            self.resetOnlineGame()
        else:
            self.OnlineGame.keyPressed(keyCode, modifier)

    def keyPressed(self, keyCode, modifier):
        if self.mode == 'MainSplash':
            self.MainSplashKeyPressed(keyCode, modifier)
        elif self.mode == 'NormalSplash':
            self.NormalSplashKeyPressed(keyCode, modifier)
        elif self.mode == 'NormalLeader':
            self.NormalLeaderKeyPressed(keyCode, modifier)
        elif self.mode == 'CustomSplash':
            self.CustomSplashKeyPressed(keyCode, modifier)
        elif self.mode == 'CustomLeader':
            self.CustomLeaderKeyPressed(keyCode, modifier)
        elif self.mode == 'VersusSplash':
            self.VersusSplashKeyPressed(keyCode, modifier)
        elif self.mode == 'OnlineSplash':
            self.OnlineSplashKeyPressed(keyCode, modifier)
        elif self.mode == 'NormalGame':
            self.NormalGameKeyPressed(keyCode, modifier)
        elif self.mode == 'CustomGame':
            self.CustomGameKeyPressed(keyCode, modifier)
        elif self.mode == 'VersusGame':
            self.VersusGameKeyPressed(keyCode, modifier)
        elif self.mode == 'OnlineGame':
            self.OnlineGameKeyPressed(keyCode, modifier)

    def keyReleased(self, keyCode, modifier):
        if self.mode == 'NormalGame':
            self.NormalGame.keyReleased(keyCode, modifier)
        elif self.mode == 'CustomGame':
            self.CustomGame.keyReleased(keyCode, modifier)
        elif self.mode == 'VersusGame':
            self.VersusGame.keyReleased(keyCode, modifier)
        elif self.mode == 'OnlineGame':
            self.OnlineGame.keyReleased(keyCode, modifier)

    def timerFired(self, dt):
        while self.server != None and self.serverMsg.qsize() > 0 and \
            self.mode != 'OnlineGame':
            msg = self.serverMsg.get(False)
            try:
                msg = msg.split()
                command = msg[0]

                if command == "myIDis":
                    playerID = msg[1]
                    self.OnlineSplash.player = playerID
                    self.OnlineGame.player = playerID
                elif command == "newPlayer":
                    # we do not need to worry about other player's ID
                    # since there is only two possible, and one is
                    # already taken by yourself
                    self.OnlineSplash.otherConnected = True
                    self.OnlineGame.otherConnected = True
                elif command == 'start':
                    self.startOnlineGame()
            except:
                self.serverMsg.task_done()

        if self.OnlineGame.quit[0] == True:
            parameter = self.OnlineGame.quit[1]
            self.quitOnlineGame()
            if parameter == 'override':
                self.OnlineSplash.otherConnected = False
                self.OnlineGame.otherConnected = False
                self.OnlineSplash.server = None
                self.OnlineGame.server = None
                self.server = None
            self.OnlineGame.quit = (False, None)

        if self.OnlineGame.reset == True:
            self.resetOnlineGame()
            self.OnlineGame.reset = False

        if self.mode == 'NormalGame':
            self.NormalGame.timerFired(dt)
            self.title = "Super Py-gon"
        elif self.mode == 'CustomGame':
            self.CustomGame.timerFired(dt)
            if self.CustomGame.isPlayingGame:
                # if user is playing a custom game, display
                # current song in title bar
                song = self.CustomGame.audioPath.split('/')[-1]
                self.title = 'Now Playing: ' + song
            else:
                self.title = "Super Py-gon"
        elif self.mode == 'VersusGame':
            self.VersusGame.timerFired(dt)
            self.title = "Super Py-gon"
        elif self.mode == 'OnlineGame':
            self.OnlineGame.timerFired(dt, self.serverMsg)
            self.title = "Super Py-gon"
        else:
            self.title = "Super Py-gon"

    def redrawAll(self, screen):
        if self.mode == 'MainSplash':
            self.MainSplash.redrawAll(screen)
        elif self.mode == 'NormalSplash':
            self.NormalSplash.redrawAll(screen)
        elif self.mode == 'NormalLeader':
            self.NormalLeader.redrawAll(screen)
        elif self.mode == 'CustomSplash':
            self.CustomSplash.redrawAll(screen)
        elif self.mode == 'CustomLeader':
            self.CustomLeader.redrawAll(screen)
        elif self.mode == 'VersusSplash':
            self.VersusSplash.redrawAll(screen)
        elif self.mode == 'OnlineSplash':
            self.OnlineSplash.redrawAll(screen)
        elif self.mode == 'NormalGame':
            self.NormalGame.redrawAll(screen)
        elif self.mode == 'CustomGame':
            self.CustomGame.redrawAll(screen)
        elif self.mode == 'VersusGame':
            self.VersusGame.redrawAll(screen)
        elif self.mode == 'OnlineGame':
            self.OnlineGame.redrawAll(screen)

    def isKeyPressed(self, key):
        # return whether a specific key is being held
        return self._keys.get(key, False)

    def __init__(self, serverMsg=None, server=None, width=1280, height=720, fps=50, title="Super Py-gon"):
        self.width = width
        self.height = height
        self.fps = fps
        self.title = title
        self.bgColor = (0,0,0)

        self.server = server
        self.serverMsg = serverMsg

        pg.init()

    def run(self):

        clock = pg.time.Clock()
        screen = pg.display.set_mode((self.width, self.height))
        # set the title of the window
        pg.display.set_caption(self.title)

        # stores all the keys currently being held down
        self._keys = dict()

        # call game-specific initialization
        self.init()

        # set program icon
        icon = pg.image.load('resources/icon.png').convert_alpha()
        pg.display.set_icon(icon)

        playing = True
        while playing:
            pg.display.set_caption(self.title)
            time = clock.tick(self.fps)
            self.timerFired(time)
            for event in pg.event.get():
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    self.mousePressed(*(event.pos))
                elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                    self.mouseReleased(*(event.pos))
                elif (event.type == pg.MOUSEMOTION and
                      event.buttons == (0, 0, 0)):
                    self.mouseMotion(*(event.pos))
                elif (event.type == pg.MOUSEMOTION and
                      event.buttons[0] == 1):
                    self.mouseDrag(*(event.pos))
                elif event.type == pg.KEYDOWN:
                    self._keys[event.key] = True
                    self.keyPressed(event.key, event.mod)
                elif event.type == pg.KEYUP:
                    self._keys[event.key] = False
                    self.keyReleased(event.key, event.mod)
                elif event.type == pg.QUIT:
                    self.NormalGame.isPlayingMusic = False
                    self.CustomGame.isPlayingMusic = False
                    self.VersusGame.isPlayingMusic = False
                    self.OnlineGame.isPlayingMusic = False
                    if self.server != None:
                        msg = 'quit override\n'
                        self.server.send(msg.encode())
                    playing = False
                    pg.quit()
            screen.fill(self.bgColor)
            self.redrawAll(screen)
            pg.display.update()

        pg.quit()

def main():
    if connected:
        serverMsg = Queue(100)
        threading.Thread(target = handleServerMsg, args = (server, serverMsg)).start()
        game = Game(serverMsg, server)
    else:
        game = Game()
    game.run()

if __name__ == '__main__':
    main()