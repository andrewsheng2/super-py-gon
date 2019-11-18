# Main splash screen of the app

import pygame as pg

class MainSplash():

    def __init__(self, width, height):
        self.width, self.height = width, height
        self.fontMedium = pg.font.Font('resources/font.ttf', 36)
        self.fontBig = pg.font.Font('resources/font.ttf', 72)
        self.super = self.fontBig.render('Super', True, (255,255,255))
        self.superRect = self.super.get_rect(center=(width // 2, height // 4))
        self.pygon = self.fontBig.render('Py-gon', True, (255,255,255))
        self.pygonRect = self.pygon.get_rect(center=(width // 2, 2*height // 5))
        message = 'Click anywhere to begin'
        self.message = self.fontMedium.render(message, True, (255,255,255))
        self.messageRect = self.message.get_rect(center=(width // 2, 4*height // 5))

    def redrawAll(self, screen):
        screen.blit(self.super, self.superRect)
        screen.blit(self.pygon, self.pygonRect)
        screen.blit(self.message, self.messageRect)