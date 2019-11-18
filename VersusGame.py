# Game screen of local multiplayer mode

import pygame as pg
import pyaudio as pa
import wave
import random
import threading

from Buttons import *
from Sprites import *

# CITATION: Threading function decorator from Stack Overflow
# https://stackoverflow.com/questions/19846332/python-threading-inside-a-class
def threaded(fn):
    # wil take a function and make it threaded
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper

class VersusGame():
    # Note1: I could inherit from NormalGame, but it will only inherit
    # one function, playMusic() and since a lot of properties in the class
    # are different (ex. self.p1Arr/p2Arr instead of self.arrow)
    # I felt would be better just to have all the code without inheritance

    # Note2: Cheat code to skip obstacle and beta features (hard mode)
    # are disabled to avoid unexpected behavior

    def __init__(self, width, height):
        # initializes all variables needed for the game
        self.width, self.height = width, height
        self.fontSmall = pg.font.Font('resources/font.ttf', 24)
        self.fontMedium = pg.font.Font('resources/font.ttf', 36)
        self.fontBig = pg.font.Font('resources/font.ttf', 72)
        # initialize player 1's data
        self.p1CH = CenterHexagon(width // 2, height)
        self.p1Arr = Arrow(width // 2, height)
        self.p1MovingLeft = False
        self.p1MovingRight = False
        self.p1Playing = True
        self.p1Screen = pg.Surface((width // 2, height))
        # initialize player 2's data
        self.p2CH = CenterHexagon(width // 2, height)
        self.p2Arr = Arrow(width // 2, height)
        self.p2MovingLeft = False
        self.p2MovingRight = False
        self.p2Playing = True
        self.p2Screen = pg.Surface((width // 2, height))
        self.possibleObstacles = [ ]
        for i in range(1,7):
            path = 'resources/obstacle' + str(i) + '.png'
            image = pg.image.load(path).convert_alpha()
            self.possibleObstacles.append(image)
        self.obstacles = [ ]
        self.timeElapsed = 0
        self.timeGap = 0
        self.isPlayingGame = False
        self.isPlayingMusic = False
        self.donePlayingMusic = False
        self.scale = 0.96
        self.waitTime = 1920
        self.flash = False
        self.audioPath = 'resources/Hexagon.wav'
        self.invincible = False
        self.backButton = BackButton(width, height)

    @threaded
    def playMusic(self):
        # plays .wav file and will restart when done playing

        CHUNK = 1024

        audio = wave.open(self.audioPath, 'rb')
        p = pa.PyAudio()

        # open stream based on the wave file
        stream = p.open(format =
                        p.get_format_from_width(audio.getsampwidth()),
                        channels = audio.getnchannels(),
                        rate = audio.getframerate(),
                        output = True)

        data = audio.readframes(CHUNK)

        self.donePlayingMusic = False

        while self.isPlayingMusic and len(data) > 0:
            # writing to the stream plays the sound.
            stream.write(data)
            data = audio.readframes(CHUNK)

        stream.stop_stream()
        stream.close()
        p.terminate()

        self.donePlayingMusic = True

    @threaded
    def generateObstacle(self):
        # choose a random obstacle to generate
        index = random.randint(0,11)
        if index < 12:
            index %= 6
            obstacle = self.possibleObstacles[index]
        elif index >= 12:
            index -= 6
            obstacle = self.possibleObstacles[index]
        self.obstacles.append(Obstacle(obstacle, self.width // 2, self.height))

    def keyPressed(self, keyCode, modifier):
        # execute game commands when certain keys are pressed
        if self.isPlayingGame:
            if keyCode == pg.K_a:
                self.p1MovingLeft = True
            elif keyCode == pg.K_d:
                self.p1MovingRight = True
            if keyCode == pg.K_LEFT:
                self.p2MovingLeft = True
            elif keyCode == pg.K_RIGHT:
                self.p2MovingRight = True
            elif keyCode == pg.K_i:
                self.invincible = not self.invincible

    def keyReleased(self, keyCode, modifier):
        # stop moving arrow when key is not pressed
        if self.isPlayingGame:
            if keyCode == pg.K_a:
                self.p1MovingLeft = False
            if keyCode == pg.K_d:
                self.p1MovingRight = False
            if keyCode == pg.K_LEFT:
                self.p2MovingLeft = False
            if keyCode == pg.K_RIGHT:
                self.p2MovingRight = False

    def scaleObstacles(self):
        # scales all obstacles and checks for collision between
        # arrow and obstacle and center hexagon and obstacle
        for obstacle in self.obstacles:
            obstacle.scale *= self.scale
        if self.obstacles != []:
            obstacle = self.obstacles[0]
            if pg.sprite.collide_mask(self.p1Arr, obstacle) != None:
                if not self.invincible:
                    self.isPlayingGame = False
                    self.isPlayingMusic = False
                    self.p1MovingLeft = False
                    self.p1MovingRight = False
                    self.p1Playing = False
                    self.flash = True
            if pg.sprite.collide_mask(self.p2Arr, obstacle) != None:
                if not self.invincible:
                    self.isPlayingGame = False
                    self.isPlayingMusic = False
                    self.p2MovingLeft = False
                    self.p2MovingRight = False
                    self.p2Playing = False
                    self.flash = True
            if pg.sprite.collide_mask(self.p1CH, obstacle) != None and \
                pg.sprite.collide_mask(self.p2CH, obstacle) != None:
                self.obstacles.pop(0)

    def moveP1Arrow(self, direction):
        # changes angle of arrow
        if direction == 'left':
            self.p1Arr.angle += 10
        elif direction == 'right':
            self.p1Arr.angle -= 10
        self.p1Arr.angle %= 360

    def moveP2Arrow(self, direction):
        # changes angle of arrow
        if direction == 'left':
            self.p2Arr.angle += 10
        elif direction == 'right':
            self.p2Arr.angle -= 10
        self.p2Arr.angle %= 360

    def timerFired(self, dt):
        # scales obstacles, moves arrow, and replays music when done playing
        if self.isPlayingGame:
            self.timeElapsed += dt
            self.timeGap += dt
            self.scaleObstacles()
            if self.timeGap > self.waitTime:
                self.timeGap = 0
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

    def drawGameOver(self, screen):
        # draw game over screen on top of game screen
        secondsElapsed = self.timeElapsed / 1000
        timeText = '%0.2f' %secondsElapsed
        background = pg.Surface((self.width, self.height), pg.SRCALPHA)
        background.fill((0,0,0,100))
        textBackground = pg.Surface((self.width, 3*self.height // 5), pg.SRCALPHA)
        textBackground.fill((0,0,0,160))
        textBackgroundRect = textBackground.get_rect()
        textBackgroundRect.midleft = (0, self.height // 2)
        screen.blit(background, (0,0))
        screen.blit(textBackground, textBackgroundRect)
        if not self.p1Playing and not self.p2Playing:
            winnerText = 'Tie!'
        elif self.p1Playing and not self.p2Playing:
            winnerText = 'Player 1 wins!'
        elif self.p2Playing and not self.p1Playing:
            winnerText = 'Player 2 wins!'
        winner = self.fontBig.render(winnerText, True, (255,255,255))
        winnerRect = winner.get_rect(center=(self.width // 2, self.height // 3))
        screen.blit(winner, winnerRect)
        restartText = 'Click to reset'
        restartMessage = self.fontMedium.render(restartText, True, (255,255,255))
        restartRect = restartMessage.get_rect(center=(self.width // 2, 2*self.height // 3))
        screen.blit(restartMessage, restartRect)
        timeText = "Time passed: " + timeText
        time = self.fontMedium.render(timeText, True, (255,255,255))
        timeRect = time.get_rect(center=(self.width // 2, self.height // 2))
        screen.blit(time, timeRect)
        self.backButton.draw(screen)
        pg.display.update()

    def drawPlayer1(self):
        # draw player 1's sprites and screen
        self.p1Screen.fill((0,0,0))
        self.p1Arr.draw(self.p1Screen)
        for obstacle in self.obstacles:
            obstacle.draw(self.p1Screen)
        self.p1CH.draw(self.p1Screen)
        secondsElapsed = self.timeElapsed / 1000
        timeText = '%0.2f' %secondsElapsed
        if self.isPlayingGame:
            time = self.fontMedium.render(timeText, True, (255,255,255))
            timeRect = time.get_rect(center=(self.width // 4, 5*self.height // 6))
            self.p1Screen.blit(time, timeRect)
        if self.invincible:
            invincible = self.fontSmall.render('Invincible', True, (255,255,255))
            margin = 25
            self.p1Screen.blit(invincible, (margin, 11*self.height // 12))

    def drawPlayer2(self):
        # draw player 2's sprites and screen
        self.p2Screen.fill((0,0,0))
        self.p2Arr.draw(self.p2Screen)
        for obstacle in self.obstacles:
            obstacle.draw(self.p2Screen)
        self.p2CH.draw(self.p2Screen)
        secondsElapsed = self.timeElapsed / 1000
        timeText = '%0.2f' %secondsElapsed
        if self.isPlayingGame:
            time = self.fontMedium.render(timeText, True, (255,255,255))
            timeRect = time.get_rect(center=(self.width // 4, 5*self.height // 6))
            self.p2Screen.blit(time, timeRect)
        if self.invincible:
            invincible = self.fontSmall.render('Invincible', True, (255,255,255))
            margin = 25
            self.p2Screen.blit(invincible, (margin, 11*self.height // 12))

    def redrawAll(self, screen):
        # draw game screen
        self.drawPlayer1()
        self.drawPlayer2()
        screen.blit(self.p1Screen, (0,0))
        screen.blit(self.p2Screen, (self.width // 2, 0))
        line = pg.Surface((self.width // 100, self.height))
        line.fill((255,255,255))
        lineRect = line.get_rect()
        lineRect.midtop = (self.width // 2, 0)
        screen.blit(line, lineRect)
        if self.flash:
            screen.fill((255,255,255))
            pg.display.update()
            pg.time.delay(25)
            self.flash = False
        if not self.isPlayingGame:
            self.drawGameOver(screen)
        pg.display.update()