# Sprite classes for the game

import pygame as pg

class CenterHexagon(pg.sprite.Sprite):

    def __init__(self, width, height):
        cx, cy = width // 2, height // 2
        self.image = pg.image.load('resources/center.png').convert_alpha()
        hexWidth, hexHeight = self.image.get_size()
        scaledWidth = int(hexWidth*0.085)
        scaledHeight = int(hexHeight*0.085)
        self.image = pg.transform.scale(self.image, (scaledWidth, scaledHeight))
        self.rect = self.image.get_rect(center=(cx, cy))
        self.mask = pg.mask.from_surface(self.image)
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Arrow(pg.sprite.Sprite):

    def __init__(self, width, height):
        self.cx, self.cy = width // 2, height // 2
        self.image = pg.image.load('resources/arrow.png').convert_alpha()
        arrWidth, arrHeight = self.image.get_size()
        scaledWidth = int(arrWidth*0.085)
        scaledHeight = int(arrHeight*0.085)
        self.image = pg.transform.scale(self.image, (scaledWidth, scaledHeight))
        self.angle = 0

    def draw(self, screen):
        arrow = pg.transform.rotate(self.image, self.angle)
        self.rect = arrow.get_rect(center=(self.cx, self.cy))
        self.mask = pg.mask.from_surface(arrow)
        screen.blit(arrow, self.rect)

class Obstacle(pg.sprite.Sprite):

    def __init__(self, image, width, height):
        self.cx, self.cy = width // 2, height // 2
        self.image = image
        self.scale = 1.8
        self.angle = 0
        self.rect = self.image.get_rect(center=(self.cx, self.cy))

    def draw(self, screen):
        obWidth, obHeight = self.image.get_size()
        scaledWidth = int(obWidth*self.scale)
        scaledHeight = int(obHeight*self.scale)
        obstacleScale = pg.transform.scale(self.image, (scaledWidth, scaledHeight))
        obstacleRotate = pg.transform.rotate(obstacleScale, self.angle)
        self.rect = obstacleRotate.get_rect(center=(self.cx, self.cy))
        self.mask = pg.mask.from_surface(obstacleRotate)
        screen.blit(obstacleRotate, self.rect)