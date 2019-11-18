# Splash screen for the local multiplayer mode of the game

import pygame as pg

from Buttons import *

class VersusSplash():

    def __init__(self, width, height):
        self.width, self.height = width, height
        self.fontMedium = pg.font.Font('resources/font.ttf', 36)
        self.fontBig = pg.font.Font('resources/font.ttf', 72)
        self.versusText = self.fontBig.render('Versus (Local)', True, (255,255,255))
        self.versusRect = self.versusText.get_rect(center=(width // 2, height // 5))
        message = 'Click to start'
        self.message = self.fontMedium.render(message, True, (255,255,255))
        self.messageRect = self.message.get_rect(center=(width // 2, 4*height // 5))
        player1 = "Player 1 (Left): 'A' and 'D' keys"
        player2 = "Player 2 (Right): L and R arrows"
        self.player1 = self.fontMedium.render(player1, True, (255,255,255))
        self.player2 = self.fontMedium.render(player2, True, (255,255,255))
        self.player1Rect = self.player1.get_rect(center=(width // 2, 4*height//9))
        self.player2Rect = self.player2.get_rect(center=(width // 2, 5*height//9))
        self.backButton = BackButton(width, height)
        self.leftButton = LeftButton(width, height)
        self.rightButton = RightButton(width, height)

    def redrawAll(self, screen):
        screen.blit(self.versusText, self.versusRect)
        screen.blit(self.message, self.messageRect)
        screen.blit(self.player1, self.player1Rect)
        screen.blit(self.player2, self.player2Rect)
        self.backButton.draw(screen)
        self.leftButton.draw(screen)
        self.rightButton.draw(screen)