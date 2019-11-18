# Splash screen for the online multiplayer mode of the game

import pygame as pg

from Buttons import *

class OnlineSplash():

    def __init__(self, width, height, server):
        self.width, self.height = width, height
        self.fontMedium = pg.font.Font('resources/font.ttf', 36)
        self.fontBig = pg.font.Font('resources/font.ttf', 72)
        self.onlineText = self.fontBig.render('Versus (Online)', True, (255,255,255))
        self.onlineRect = self.onlineText.get_rect(center=(width // 2, height // 5))
        self.message = self.fontMedium.render('Click to start', True, (255,255,255))
        self.messageRect = self.message.get_rect(center=(self.width // 2, 4*self.height // 5))
        self.backButton = BackButton(width, height)
        self.leftButton = LeftButton(width, height)
        self.rightButton = RightButton(width, height)
        self.player = None
        self.otherConnected = False

        self.server = server

    def redrawAll(self, screen):
        screen.blit(self.onlineText, self.onlineRect)
        screen.blit(self.message, self.messageRect)
        if self.server == None:
            playerText = 'Unable to connect'
        elif self.server != None:
            if self.otherConnected:
                if self.player == "1":
                    playerText = 'You are player 1 (left side)'
                elif self.player == "2":
                    playerText = 'You are player 2 (right side)'
            else:
                playerText = 'Waiting for players...'
        player = self.fontMedium.render(playerText, True, (255,255,255))
        playerRect = player.get_rect(center=(self.width // 2, self.height // 2))
        screen.blit(player, playerRect)
        self.backButton.draw(screen)
        self.leftButton.draw(screen)
        self.rightButton.draw(screen)