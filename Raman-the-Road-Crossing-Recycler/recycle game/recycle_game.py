import pygame
import sys
import os
import random
import settings as setting
import mapConfig as maps
import sprites as sprite

def getFilePath():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(__file__)

class Game:
    def __init__(self):
        pygame.mixer.pre_init(44100,  -16, 1, 2048)
        pygame.mixer.set_num_channels(10)
        pygame.key.set_repeat(500, 100)
        infoObject = pygame.display.Info()
        self.modes = [infoObject.current_w, infoObject.current_h] 
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (self.modes[0] / 2 - (setting.WIDTH / 2), 
                                                            self.modes[1] / 2 - (setting.HEIGHT / 2))
        self.gameDisplay = pygame.display.set_mode((setting.WIDTH, setting.HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        pygame.key.set_repeat(500, 100)      
        self.loadData()

    def loadData(self):
        gameFolder = getFilePath()
        dataFolder = os.path.join(gameFolder, "data")
        self.mapFolder = os.path.join(dataFolder, "maps")
        imgFolder = os.path.join(dataFolder, "images")
        fontFoler = os.path.join(dataFolder, "fonts")
        self.font = os.path.join(fontFoler, setting.FONT)       
        self.playerImage = pygame.image.load(os.path.join(imgFolder, setting.PLAYERIMG)).convert_alpha()
        self.playerRotate = pygame.image.load(os.path.join(imgFolder, setting.PLAYERROTATE)).convert_alpha()
        self.playerFlip = pygame.image.load(os.path.join(imgFolder, setting.PLAYERFLIP)).convert_alpha()
        self.playerRotate1 = pygame.image.load(os.path.join(imgFolder, setting.PLAYERROTATE1)).convert_alpha()
        self.recycleImage = pygame.image.load(os.path.join(imgFolder, setting.RECYCLEBIN)).convert_alpha()
        self.heartImage = pygame.image.load(os.path.join(imgFolder, setting.HEART)).convert_alpha()
        self.hazardImage = pygame.image.load(os.path.join(imgFolder, setting.HAZARD)).convert_alpha()
        #litter
        litterImage = pygame.image.load(os.path.join(imgFolder, setting.LITTER)).convert_alpha()
        litterImage1 = pygame.image.load(os.path.join(imgFolder, setting.LITTER1)).convert_alpha()
        self.litterImages = [litterImage, litterImage1]
        #vehicles
        carImage = pygame.image.load(os.path.join(imgFolder, setting.CAR)).convert_alpha()
        carImage1 = pygame.image.load(os.path.join(imgFolder, setting.CAR1)).convert_alpha()
        self.vehicleImages = [carImage, carImage1]

        self.levels = { 1 : "map.tmx", 2 : "map1.tmx", 3 : "map3.tmx"}
        self.level = setting.DEFAULTLEVEL    
        self.lives = setting.PLAYERLIVES    
        self.score = 0

    def randomLocations(self, k, offsetX, offsetY, width, height):
        p = []
        currentPoint = (0, 0)
        rows, cols = width / setting.TILESIZE, height / setting.TILESIZE #find the num of rows, cols in spawn area, to spawn objects to
        for x in range(k):          
            while True:
                posX = random.randint(0, rows - 1) * (width / rows)
                posY = random.randint(0, cols - 1) * (height / cols)
                currentPoint = (posX + offsetX, posY + offsetY) #Add offset to account for spawn area location
                if currentPoint not in p:
                    break
            p.append(currentPoint)
            sprite.Litter(self, currentPoint[0], currentPoint[1])
            self.litter += 1

    def load(self):
        self.litter = 0
        self.timer = setting.TIME
        self.allSprites = pygame.sprite.Group()
        self.litterSprites = pygame.sprite.Group()
        self.collisionSprites = pygame.sprite.Group()
        self.vehicleSprites = pygame.sprite.Group()
        self.hazardSprites = pygame.sprite.Group()

        self.map = maps.TiledMap(os.path.join(self.mapFolder, self.levels[self.level]))
        self.mapImg = self.map.make_map()
        self.mapRect = self.mapImg.get_rect()

        for tileObject in self.map.tmxdata.objects:
            if tileObject.name == "Player":
                self.player = sprite.Player(self, tileObject.x, tileObject.y)
            if tileObject.name == "Collision":
                sprite.Obstacle(self, tileObject.x, tileObject.y, tileObject.width, tileObject.height)
            if tileObject.name == "Vehicle":
                sprite.Vehicle(self, tileObject.x,  tileObject.y, str(tileObject.type))
            if tileObject.name == "Recycle":
                self.recycleBin = sprite.Bin(self, tileObject.x, tileObject.y)
            if tileObject.name == "Spawn":
                self.randomLocations(int(tileObject.type), tileObject.x, tileObject.y, tileObject.width, tileObject.height)
          
        self.camera = maps.Camera(self.map.width, self.map.height)
        self.run()

    def panCamera(self, speed):  
        self.panner = sprite.Panner(setting.WIDTH / 2, 0)
        y = setting.HEIGHT / 2 - 10
        while y < self.map.height - (setting.HEIGHT / 2):     
            self.dt = self.clock.tick(setting.FPS) / 1000
            self.panner.rect.y = y
            self.camera.update(self.panner)     
            self.vehicleSprites.update()
            self.keyEvents()    
            self.draw(True)        
            y += speed
        return       

    def run(self):
        self.playing = True
        self.panCamera(self.map.height / setting.PANSPEED)
        while self.playing:        
           self.keyEvents()
           self.update()
           self.draw()

    def update(self):
        self.dt = self.clock.tick(setting.FPS) / 1000
        # When not panning down       
        self.allSprites.update()        
        self.camera.update(self.player)
        now = pygame.time.get_ticks()
        self.timer -= self.dt

        hits = pygame.sprite.spritecollide(self.player, self.vehicleSprites, False)
        if self.timer < 0 or hits:
            # Run out of time
            self.lives -= 1
            self.load()

        if self.lives < 1:
            # game over
            print("GAME OVER")

        # Completes a level
        if pygame.sprite.collide_rect(self.player, self.recycleBin):
            if self.player.litter >= self.litter:
                self.level += 1
                self.score += self.timer
                self.levelCompleteScreen()
                self.load()
   
        # Collects litter
        hits = pygame.sprite.spritecollide(self.player, self.litterSprites, False)
        if hits:
            self.player.litter += 1
            self.litterSprites.remove(hits[0])
            self.allSprites.remove(hits[0])
            hits[0].kill()

    def keyEvents(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

    def renderMessage(self, font, text, size, colour, x, y):
        ####render a message to the screen####
        font = pygame.font.Font(font, size)
        text_surface = font.render(text, True, colour)
        text_rect = text_surface.get_rect()
        text_rect.x = x
        text_rect.y = y
        self.gameDisplay.blit(text_surface, text_rect)
        return text_rect

    def renderObjectImage(self, k, x, y, img, increment):
        for i in range(k):
            self.gameDisplay.blit(img, (x, y))
            x += increment
        return x

    def mainMenu(self):
        self.pos = sprite.MousePos(self)
        while True:
             self.dt = self.clock.tick(setting.FPS) / 1000
             self.pos.update()
             self.keyEvents()
             if self.pos.pressed:
                 break
        return

    def levelCompleteScreen(self):
        self.pos = sprite.MousePos(self)
        self.button1 = sprite.Obstacle(self, 100, (setting.HEIGHT - 100) - self.camera.y, 600, 70)
        while True:
            self.dt = self.clock.tick(setting.FPS) / 1000
            self.vehicleSprites.update()
            self.pos.update()    
            self.keyEvents()
            if self.pos.pressed:
                break
        return

    def draw(self, pan = False, complete = False, col = setting.WHITE):
        self.gameDisplay.blit(self.mapImg, self.camera.apply_rect(self.mapRect))        
        for s in self.allSprites:
            self.gameDisplay.blit(s.image, self.camera.apply(s))

        if pan:
            self.renderMessage(self.font, "LEVEL " + str(self.level), 70, setting.WHITE, 180, setting.HEIGHT / 2 - 30)
        elif complete:
            self.renderMessage(self.font, "LEVEL", 70, setting.WHITE, 240, setting.TILESIZE)
            self.renderMessage(self.font, "COMPLETE!", 70, setting.WHITE, 140, setting.TILESIZE + 100)
            self.renderMessage(self.font, "SCORE " + str(round(self.score, 0))[:-2], 70, setting.WHITE, 140, setting.HEIGHT / 2)
            self.renderMessage(self.font, "NEXT LEVEL", 70, col, 100, setting.HEIGHT - 100)
        else:                      
            self.renderMessage(self.font, "TIME " + str(round(self.timer, 0))[:-2], 40, setting.WHITE, 270, 22)
            self.renderObjectImage(self.player.lives, 10, setting.HEIGHT - 74, self.heartImage, 74)

            percent = (self.player.litter / self.litter) * 100     
            percentX = self.renderObjectImage(self.player.litter, setting.WIDTH - 74, setting.HEIGHT - 74, self.litterImages[0], -74)
            self.renderMessage(self.font, str(round(percent, 0))[:-2] + u"%", 40, setting.WHITE, percentX - 55, setting.HEIGHT - 65)

        pygame.display.update()

if __name__ == "__main__":
    g = Game()
    while g.running:
        g.load()
    pygame.quit()
    sys.exit()
