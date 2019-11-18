# Game screen of Normal mode

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

class NormalGame():

    def __init__(self, width, height, hard=False):
        # initializes all variables needed for the game
        self.width, self.height = width, height
        self.fontSmall = pg.font.Font('resources/font.ttf', 24)
        self.fontMedium = pg.font.Font('resources/font.ttf', 36)
        self.fontBig = pg.font.Font('resources/font.ttf', 72)
        self.centerHexagon = CenterHexagon(width, height)
        self.arrow = Arrow(width, height)
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
        self.isMovingLeft = False
        self.isMovingRight = False
        self.waitTime = 700
        self.flash = False
        self.hardMode = hard
        self.audioPath = 'resources/Hexagon.wav'
        self.invincible = False
        self.highScores = self.getHighScores()
        self.backButton = BackButton(width, height)
    
    def getHighScores(self):
        # get high scores out of text file stored on computer
        scores = self.readFile('data/HighScoresNormal.txt').splitlines()
        highScores = dict()
        if len(scores) == 0:
            highScores[0] = 'No data'
        else:
            for time in scores:
                highScores[float(time)] = 'Hexagon.wav'
        return highScores

    def readFile(self, path):
    # from 15-112 course notes
    # https://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
        # I placed readFile() and writeFile() inside the class so
        # they can get inherited in CustomGame, rather than outside
        with open(path, "rt") as f:
            return f.read()

    def writeFile(self, path, contents):
    # from 15-112 course notes
    # https://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
        with open(path, "wt") as f:
            f.write(contents)

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
        self.obstacles.append(Obstacle(obstacle, self.width, self.height))

    def mousePressed(self, x, y):
        # start moving arrow in certain direction
        # depending on which side of screen is clicked
        if x < self.width // 2:
            self.isMovingLeft = True
        elif x >= self.width // 2:
            self.isMovingRight = True

    def mouseReleased(self, x, y):
        # stop moving arrow when mouse is not clicked
        if self.isPlayingGame:
            self.isMovingLeft = False
            self.isMovingRight = False

    def keyPressed(self, keyCode, modifier):
        # execute game commands when certain keys are pressed
        if self.isPlayingGame:
            if keyCode == pg.K_LEFT:
                self.isMovingLeft = True
            elif keyCode == pg.K_RIGHT:
                self.isMovingRight = True
            elif keyCode == pg.K_h:
                self.hardMode = not self.hardMode
            elif keyCode == pg.K_i:
                self.invincible = not self.invincible
        elif keyCode == pg.K_s:
            self.obstacles.pop(0)
            self.isPlayingGame = True
            self.isPlayingMusic = True
            self.playMusic()

    def keyReleased(self, keyCode, modifier):
        # stop moving arrow when key is not pressed
        if self.isPlayingGame:
            if keyCode == pg.K_LEFT:
                self.isMovingLeft = False
            if keyCode == pg.K_RIGHT:
                self.isMovingRight = False

    def storeHighScores(self):
        # overwrites text file with updated high scores
        while len(self.highScores) > 5:
            smallest = min(self.highScores)
            del self.highScores[smallest]
        scores = [ ]
        for item in self.highScores:
            scores.append(str(item))
        scoresText = '\n'.join(scores)
        self.writeFile('data/HighScoresNormal.txt', scoresText)

    def scaleObstacles(self):
        # scales all obstacles and checks for collision between
        # arrow and obstacle and center hexagon and obstacle
        i = 1
        for obstacle in self.obstacles:
            obstacle.scale *= self.scale
            if self.hardMode == True:
                self.waitTime = 900
                obstacle.angle += 1*i
                obstacle.angle %= 360
                i *= -1
        if self.obstacles != []:
            obstacle = self.obstacles[0]
            if pg.sprite.collide_mask(self.arrow, obstacle) != None:
                if not self.invincible:
                    self.isPlayingGame = False
                    self.isPlayingMusic = False
                    self.isMovingLeft = False
                    self.isMovingRight = False
                    self.flash = True
                    time = self.timeElapsed / 1000
                    song = self.audioPath.split('/')[-1]
                    self.highScores[time] = song
                    self.storeHighScores()
            elif pg.sprite.collide_mask(self.centerHexagon, obstacle) != None:
                self.obstacles.pop(0)

    def moveArrow(self, direction):
        # changes angle of arrow
        if direction == 'left':
            self.arrow.angle += 10
        elif direction == 'right':
            self.arrow.angle -= 10
        self.arrow.angle %= 360

    def timerFired(self, dt):
        # scales obstacles, moves arrow, and replays music when done playing
        if self.isPlayingGame:
            self.timeElapsed += dt
            self.timeGap += dt
            self.scaleObstacles()
            if self.timeGap > self.waitTime:
                self.timeGap = 0
                self.generateObstacle()
            if self.isMovingLeft:
                self.moveArrow('left')
            elif self.isMovingRight:
                self.moveArrow('right')
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
        gameOver = self.fontBig.render('Game Over', True, (255,255,255))
        gameOverRect = gameOver.get_rect(center=(self.width // 2, self.height // 3))
        screen.blit(gameOver, gameOverRect)
        restartText = 'Click to reset'
        restartMessage = self.fontMedium.render(restartText, True, (255,255,255))
        restartRect = restartMessage.get_rect(center=(self.width // 2, 2*self.height // 3))
        screen.blit(restartMessage, restartRect)
        timeText = "Your time: " + timeText
        time = self.fontMedium.render(timeText, True, (255,255,255))
        timeRect = time.get_rect(center=(self.width // 2, self.height // 2))
        screen.blit(time, timeRect)
        self.backButton.draw(screen)
        pg.display.update()

    def redrawAll(self, screen):
        # draw game screen
        self.arrow.draw(screen)
        for obstacle in self.obstacles:
            obstacle.draw(screen)
        self.centerHexagon.draw(screen)
        secondsElapsed = self.timeElapsed / 1000
        timeText = '%0.2f' %secondsElapsed
        if self.isPlayingGame:
            time = self.fontBig.render(timeText, True, (255,255,255))
            timeRect = time.get_rect(center=(self.width // 2, 5*self.height // 6))
            screen.blit(time, timeRect)
        if self.invincible:
            invincible = self.fontSmall.render('Invincible', True, (255,255,255))
            margin = 25
            screen.blit(invincible, (margin, 11*self.height // 12))
        if self.flash:
            screen.fill((255,255,255))
            pg.display.update()
            pg.time.delay(25)
            self.flash = False
        if not self.isPlayingGame:
            self.drawGameOver(screen)
        pg.display.update()