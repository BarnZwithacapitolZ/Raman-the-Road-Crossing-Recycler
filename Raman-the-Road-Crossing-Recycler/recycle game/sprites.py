import pygame
import settings as setting
from mapConfig import collide_hit_rect
vec = pygame.math.Vector2

def collide_with_walls(sprite, group, direction):
        if direction == "x":
           hits = pygame.sprite.spritecollide(sprite, group, False, collide_hit_rect)
           if hits:
               if hits[0].rect.centerx > sprite.hit_rect.centerx:
                   sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
               if  hits[0].rect.centerx < sprite.hit_rect.centerx:
                   sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
               sprite.vel.x = 0
               sprite.hit_rect.centerx = sprite.pos.x

        if direction == "y":
           hits = pygame.sprite.spritecollide(sprite, group, False, collide_hit_rect)
           if hits:
               if hits[0].rect.centery > sprite.hit_rect.centery:
                   sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
               if hits[0].rect.centery < sprite.hit_rect.centery:
                   sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
               sprite.vel.y = 0
               sprite.hit_rect.centery = sprite.pos.y

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.allSprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.playerImage     
        self.rect = self.image.get_rect()
        self.hit_rect = pygame.Rect(0, 0, 62, 103)
        self.hit_rect.center = self.rect.center
        self.pos = vec(x, y) 
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.rot = 0
        self.lives = game.lives
        self.litter = 0

    def getKeys(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.acc = vec(setting.PLAYERSPEED, 0).rotate(-self.rot)

    def update(self):
        self.acc = (0, 0)
        self.getKeys()
        mx, my = pygame.mouse.get_pos()
        mx -= self.game.camera.x
        my -= self.game.camera.y
        self.rot = ((mx, my) - self.pos).angle_to(vec(1, 0))
        
        if self.rot > -110 and self.rot < -70:
            self.image = self.game.playerImage
        elif self.rot > -70 and self.rot < 10:
            self.image = pygame.transform.flip(self.game.playerRotate, True, False)
        elif self.rot > 10 and self.rot < 80:
            self.image = self.game.playerRotate1
        elif self.rot > 80 and self.rot < 110:
            self.image = self.game.playerFlip
        elif self.rot > 110 and self.rot < 170:
            self.image = pygame.transform.flip(self.game.playerRotate1, True, False)
        else:
            self.image = self.game.playerRotate
    
        self.rect = self.image.get_rect()
        self.rect.center = self.pos      
        self.acc += self.vel * setting.PLAYERFRICTION 
        self.vel += self.acc * self.game.dt
        self.pos += self.vel * self.game.dt + setting.PLAYERINITIALACC * self.acc * self.game.dt ** 2

        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.collisionSprites, "x")      
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.collisionSprites, "y")
        self.rect.center = self.hit_rect.center

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.collisionSprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pygame.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

class Panner(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.rect = pygame.Rect(x, y, 10, 10)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
