import pygame
import random
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

        #print(self.rot, self.acc, self.vel, self.pos)

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
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(x, y, 10, 10)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

class Bin(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.allSprites, game.collisionSprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = game.recycleImage
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Litter(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.allSprites, game.litterSprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        selection = random.randint(0, len(game.litterImages) - 1)
        self.image = game.litterImages[selection]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Vehicle(pygame.sprite.Sprite):
    def __init__(self, game, x, y, direction):
        self.groups = game.allSprites, game.collisionSprites, game.vehicleSprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.direction = direction
        selection = random.randint(0, len(game.vehicleImages) - 1)
        self.image = game.vehicleImages[selection]
        self.speed = random.randint(3, 5)

        if direction == "left":
           self.image = pygame.transform.flip(game.vehicleImages[selection], True, False)
           self.speed = -self.speed
           
        self.rect = self.image.get_rect()
        self.x = x
        self.rect.x = x
        self.rect.y = y
        
    def remove(self):
        self.game.collisionSprites.remove(self)
        self.game.allSprites.remove(self)
        Vehicle(self.game, self.x, self.rect.y, self.direction)
        for hazard in self.game.hazardSprites:
            if hazard in self.game.hazardSprites:
                self.game.hazardSprites.remove(hazard)
                self.game.allSprites.remove(hazard)
                hazard.kill()
        self.kill()

    def update(self):
        self.rect.x += self.speed  
        if (self.rect.x > setting.WIDTH and self.direction == "right"):
            self.remove()
        elif (self.rect.x > setting.WIDTH / 2 and self.direction == "right"):
            Hazard(self.game, 0 + setting.TILESIZE, self.rect.y)

        if (self.rect.x < 0 - self.rect.width and self.direction == "left"):
            self.remove()
        elif (self.rect.x < setting.WIDTH / 2 - self.rect.width and self.direction == "left"):
            Hazard(self.game, setting.WIDTH - (setting.TILESIZE * 2), self.rect.y)

class Hazard(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.allSprites, game.hazardSprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = game.hazardImage
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class MousePos(pygame.sprite.Sprite):
    def __init__(self, game, messages):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.messages = messages
        self.rect = pygame.Rect(0, 0, setting.TILESIZE, setting.TILESIZE)
        self.x = 0
        self.y = 0
        self.rect.x = 0
        self.rect.y = 0
        self.pressed = False  

    def getMouse(self):
        if pygame.mouse.get_pressed()[0]:
                self.pressed = True

    def getColor(self, col):
        for key, value in self.messages.items():
                if key == "colorMessage":
                    self.messages[key][3] = col

    def update(self):
        mx, my = pygame.mouse.get_pos()
        mx -= self.game.camera.x
        my -= self.game.camera.y
        self.rect.centerx = mx
        self.rect.centery = my
        color = setting.WHITE
        if pygame.sprite.collide_rect(self, self.game.button1):
            color = setting.RED
            self.getMouse()
        self.getColor(color)
        self.game.draw(self.messages, True)


        