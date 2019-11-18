# Leaderboard screen for the Custom mode of the game

import pygame as pg

from Buttons import *

class CustomLeader():

    def __init__(self, width, height):
        self.width, self.height = width, height
        self.fontMedium = pg.font.Font('resources/font.ttf', 36)
        self.fontBig = pg.font.Font('resources/font.ttf', 72)
        self.leaderboard = self.fontBig.render('Leaderboard', True, (255,255,255))
        self.leaderboardRect = self.leaderboard.get_rect(center=(width // 2, height // 7))
        self.highScores = dict()
        self.backButton = BackButton(width, height)

    def redrawAll(self, screen):
        screen.blit(self.leaderboard, self.leaderboardRect)
        scores = list(self.highScores.keys())
        scores.sort()
        scores.reverse()
        marginX = 250
        y = 200
        if len(scores) == 0 or scores[0] == 0:
            text = self.fontBig.render('No data', True, (255,255,255))
            textRect = text.get_rect(center=(self.width // 2, 4*self.height // 7))
            screen.blit(text, textRect)
        for i in range(len(scores)):
            time = scores[i]
            song = self.highScores[time]
            if len(song) > 20:
                song = '...' + song[-16:]
            if time != 0:
                item = '%d. %0.2f - %s' %(i+1, time, song)
                score = self.fontMedium.render(item, True, (255,255,255))
                screen.blit(score, (marginX, y))
                y += 100
        self.backButton.draw(screen)