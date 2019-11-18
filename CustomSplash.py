# Splash screen for the Custom mode of the game

import pygame as pg

from Buttons import *

class CustomSplash():

    def __init__(self, width, height):
        self.width, self.height = width, height
        self.fontMedium = pg.font.Font('resources/font.ttf', 36)
        self.fontBig = pg.font.Font('resources/font.ttf', 72)
        self.customText = self.fontBig.render('Custom', True, (255,255,255))
        self.customRect = self.customText.get_rect(center=(width // 2, height // 5))
        message = 'Click to start'
        self.message = self.fontMedium.render(message, True, (255,255,255))
        self.messageRect = self.message.get_rect(center=(width // 2, 4*height // 5))
        self.highScores = dict()
        self.backButton = BackButton(width, height)
        self.leftButton = LeftButton(width, height)
        self.rightButton = RightButton(width, height)
        self.leaderButton = LeaderButton(width, height)

    def redrawAll(self, screen):
        screen.blit(self.customText, self.customRect)
        screen.blit(self.message, self.messageRect)
        bestTime = max(self.highScores)
        timeText = 'Best time: %0.2f' %bestTime
        time = self.fontMedium.render(timeText, True, (255,255,255))
        timeRect = time.get_rect(center=(self.width // 2, self.height // 2))
        screen.blit(time, timeRect)
        self.backButton.draw(screen)
        self.leftButton.draw(screen)
        self.rightButton.draw(screen)
        self.leaderButton.draw(screen)