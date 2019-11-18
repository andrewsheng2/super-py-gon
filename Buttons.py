# Button classes for the game

import pygame as pg

class Button(pg.sprite.Sprite):
    
    def __init__(self, width, height):
        self.width, self.height = width, height

    def draw(self, screen):
        screen.blit(self.button, self.rect)

class BackButton(Button):

    def __init__(self, width, height):
        super().__init__(width, height)
        self.button = pg.image.load('resources/back.png').convert_alpha()
        self.rect = self.button.get_rect()
        margin = self.width // 40
        self.rect.topleft = (margin, margin)

class LeftButton(Button):
    
    def __init__(self, width, height):
        super().__init__(width, height)
        self.button = pg.image.load('resources/left.png').convert_alpha()
        self.rect = self.button.get_rect()
        self.rect.midleft = (width // 12, 4*height // 5)

class RightButton(Button):
    
    def __init__(self, width, height):
        super().__init__(width, height)
        self.button = pg.image.load('resources/right.png').convert_alpha()
        self.rect = self.button.get_rect()
        self.rect.midright = (11*width // 12, 4*height // 5)

class LeaderButton(Button):

    def __init__(self, width, height):
        super().__init__(width, height)
        font = pg.font.Font('resources/font.ttf', 24)
        self.button = font.render('Leaderboard', True, (255,255,255))
        self.rect = self.button.get_rect()
        margin = self.width // 50
        self.rect.topright = (width - margin, margin)