# Game screen for online multiplayer mode

import pygame as pg
import pyaudio as pa
import wave
import random
import threading

from Buttons import *
from Sprites import *

from VersusGame import *

# CITATION: Threading function decorator from Stack Overflow
# https://stackoverflow.com/questions/19846332/python-threading-inside-a-class
def threaded(fn):
    # wil take a function and make it threaded
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper

class OnlineGame(VersusGame):
    # Note: For how I implemented the online game, only player 1
    # will be generating obstacles, player 2 will receive which
    # obstacles have been generated

    def __init__(self, width, height, server):
        # initializes all variables needed for the game
        super().__init__(width, height)
        self.quit = (False, None)
        self.reset = False

        self.player = None
        self.otherConnected = False

        self.server = server

    @threaded
    def generateObstacle(self):
        # choose a random obstacle to generate (player 1 only)
        if self.player == "1":
            index = random.randint(0,11)
            if index < 12:
                index %= 6
                obstacle = self.possibleObstacles[index]
            elif index >= 12:
                index -= 6
                obstacle = self.possibleObstacles[index]
            msg = 'new ' + str(index) + '\n'
            self.server.send(msg.encode())
            self.obstacles.append(Obstacle(obstacle, self.width // 2, self.height))

    def keyPressed(self, keyCode, modifier):
        # execute game commands when certain keys are pressed
        if self.isPlayingGame:
            if self.player == "1":
                if keyCode == pg.K_LEFT:
                    self.p1MovingLeft = True
                    msg = 'move left\n'
                    self.server.send(msg.encode())
                elif keyCode == pg.K_RIGHT:
                    self.p1MovingRight = True
                    msg = 'move right\n'
                    self.server.send(msg.encode())
            elif self.player == "2":
                if keyCode == pg.K_LEFT:
                    self.p2MovingLeft = True
                    msg = 'move left\n'
                    self.server.send(msg.encode())
                elif keyCode == pg.K_RIGHT:
                    self.p2MovingRight = True
                    msg = 'move right\n'
                    self.server.send(msg.encode())
            if keyCode == pg.K_i:
                msg = 'invincible toggle\n'
                self.server.send(msg.encode())
                self.invincible = not self.invincible

    def keyReleased(self, keyCode, modifier):
        # stop moving arrow when key is not pressed
        if self.isPlayingGame:
            if self.player == "1":
                if keyCode == pg.K_LEFT:
                    self.p1MovingLeft = False
                    msg = 'stop left\n'
                    self.server.send(msg.encode())
                elif keyCode == pg.K_RIGHT:
                    self.p1MovingRight = False
                    msg = 'stop right\n'
                    self.server.send(msg.encode())
            elif self.player == "2":
                if keyCode == pg.K_LEFT:
                    self.p2MovingLeft = False
                    msg = 'stop left\n'
                    self.server.send(msg.encode())
                elif keyCode == pg.K_RIGHT:
                    self.p2MovingRight = False
                    msg = 'stop right\n'
                    self.server.send(msg.encode())

    def scaleObstacles(self):
        # scales all obstacles and checks for collision between
        # arrow and obstacle and center hexagon and obstacle
        for obstacle in self.obstacles:
            obstacle.scale *= self.scale
        if self.obstacles != []:
            obstacle = self.obstacles[0]
            if self.player == "1":
                if pg.sprite.collide_mask(self.p1Arr, obstacle) != None:
                    if not self.invincible:
                        self.isPlayingGame = False
                        self.isPlayingMusic = False
                        self.p1MovingLeft = False
                        self.p1MovingRight = False
                        self.p1Playing = False
                        self.flash = True
                        msg = 'lost game\n'
                        self.server.send(msg.encode())
            elif self.player == "2":
                if pg.sprite.collide_mask(self.p2Arr, obstacle) != None:
                    if not self.invincible:
                        self.isPlayingGame = False
                        self.isPlayingMusic = False
                        self.p2MovingLeft = False
                        self.p2MovingRight = False
                        self.p2Playing = False
                        self.flash = True
                        msg = 'lost game\n'
                        self.server.send(msg.encode())
            if pg.sprite.collide_mask(self.p1CH, obstacle) != None and \
                pg.sprite.collide_mask(self.p2CH, obstacle) != None:
                self.obstacles.pop(0)

    def timerFired(self, dt, serverMsg):
        while self.server != None and serverMsg.qsize() > 0:
            msg = serverMsg.get(False)
            try:
                msg = msg.split()
                command = msg[0]

                if command == "new":
                    index = int(msg[2])
                    obstacle = self.possibleObstacles[index]
                    self.obstacles.append(Obstacle(obstacle, self.width // 2, self.height))
                elif command == "move":
                    direction = msg[2]
                    if self.player == "1":
                        if direction == "left":
                            self.p2MovingLeft = True
                        elif direction == "right":
                            self.p2MovingRight = True
                    elif self.player == "2":
                        if direction == "left":
                            self.p1MovingLeft = True
                        elif direction == "right":
                            self.p1MovingRight = True
                elif command == "stop":
                    direction = msg[2]
                    if self.player == "1":
                        if direction == "left":
                            self.p2MovingLeft = False
                        elif direction == "right":
                            self.p2MovingRight = False
                    elif self.player == "2":
                        if direction == "left":
                            self.p1MovingLeft = False
                        elif direction == "right":
                            self.p1MovingRight = False
                elif command == "lost":
                    self.isPlayingGame = False
                    self.isPlayingMusic = False
                    self.p1MovingLeft = False
                    self.p1MovingRight = False
                    self.p2MovingLeft = False
                    self.p2MovingRight = False
                    self.flash = True
                    player = msg[1]
                    if player == "1":
                        self.p1Playing = False
                    elif player == "2":
                        self.p2Playing = False
                elif command == 'invincible':
                    self.invincible = not self.invincible
                elif command == 'quit':
                    parameter = msg[2]
                    if parameter == 'override':
                        self.quit = (True, 'override')
                    else:
                        self.quit = (True, None)
                elif command == 'reset':
                    self.reset = True

            except:
                serverMsg.task_done()

        # scales obstacles, moves arrow, and replays music when done playing
        if self.isPlayingGame:
            self.timeElapsed += dt
            self.timeGap += dt
            self.scaleObstacles()
            if self.timeGap > self.waitTime:
                self.timeGap = 0
                if self.player == "1":
                    self.generateObstacle()
            if self.p1MovingLeft:
                self.moveP1Arrow('left')
            elif self.p1MovingRight:
                self.moveP1Arrow('right')
            if self.p2MovingLeft:
                self.moveP2Arrow('left')
            elif self.p2MovingRight:
                self.moveP2Arrow('right')
            if self.isPlayingMusic and self.donePlayingMusic:
                self.playMusic()
                self.donePlayingMusic = False