import pygame
import sys
import os
import random
import settings as setting
import mapConfig as maps
import sprites as sprite

def getFilePath():
    if getattr(sys, 'frozen', False): #for when .exe
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
                                                            self.modes[1] / 2 - (setting.HEIGHT / 2)) #position display to monitor centre
        self.gameDisplay = pygame.display.set_mode((setting.WIDTH, setting.HEIGHT))     
        self.fadeSurface = pygame.Surface((setting.WIDTH, setting.HEIGHT)) #for ontop of game display
        self.clock = pygame.time.Clock()
        self.running = True
        pygame.key.set_repeat(500, 100)     
        pygame.display.set_caption(setting.TITLE)
        self.loadData()

    def loadData(self):
        #only load once, during game initialisation
        gameFolder = getFilePath()
        dataFolder = os.path.join(gameFolder, "data")
        self.mapFolder = os.path.join(dataFolder, "maps")
        imgFolder = os.path.join(dataFolder, "images")
        fontFoler = os.path.join(dataFolder, "fonts")
        self.font = os.path.join(fontFoler, setting.FONT)       
        self.playerImage = pygame.image.load(os.path.join(imgFolder, setting.PLAYERIMG)).convert_alpha()
        self.playerGraveImage = pygame.image.load(os.path.join(imgFolder, setting.HUD["grave"])).convert_alpha()
        self.playerRotate = pygame.image.load(os.path.join(imgFolder, setting.PLAYERROTATE)).convert_alpha()
        self.playerFlip = pygame.image.load(os.path.join(imgFolder, setting.PLAYERFLIP)).convert_alpha()
        self.playerRotate1 = pygame.image.load(os.path.join(imgFolder, setting.PLAYERROTATE1)).convert_alpha()
        self.recycleImage = pygame.image.load(os.path.join(imgFolder, setting.RECYCLEBIN)).convert_alpha()
        self.heartImage = pygame.image.load(os.path.join(imgFolder, setting.HUD["heart"])).convert_alpha()
        self.hazardImage = pygame.image.load(os.path.join(imgFolder, setting.HUD["hazard"])).convert_alpha()
        self.titleImage = pygame.image.load(os.path.join(imgFolder, setting.HUD["title"])).convert_alpha()
        logo = pygame.image.load(os.path.join(imgFolder, setting.ICON)).convert_alpha()
        pygame.display.set_icon(logo)
        #litter
        self.litterImages = self.getImage(imgFolder, setting.LITTER)
        #vehicles
        self.vehicleImages = self.getImage(imgFolder, setting.VEHICLES)
        #levels
        self.levels = { 0 : "menu.tmx", 1 : "map.tmx", 2 : "map1.tmx", 3 : "map2.tmx"}
        self.level = setting.DEFAULTLEVEL    
        self.lives = setting.PLAYERLIVES    
        self.score = setting.DEFAULTSCORE    
        self.showInfo("data/images/infoRaman.png")
        self.showInfo("data/images/info.png")
        self.showInfo("data/images/infoStory.png")
        self.load(True) #run game

    def getImage(self, folder, imageDict):
        imgList = []
        for image in imageDict.values():
            img = pygame.image.load(os.path.join(folder, image)).convert_alpha()
            imgList.append(img)
        return imgList

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

    def load(self, menu = False):
        self.litter = 0
        self.timer = setting.TIME
        #Sprite and object groups
        self.allSprites = pygame.sprite.Group()
        self.litterSprites = pygame.sprite.Group()
        self.collisionSprites = pygame.sprite.Group()
        self.vehicleSprites = pygame.sprite.Group()
        self.hazardSprites = pygame.sprite.Group()

        self.map = maps.TiledMap(os.path.join(self.mapFolder, self.levels[self.level]))
        self.mapImg = self.map.make_map()
        self.mapRect = self.mapImg.get_rect() #for width, height

        for tileObject in self.map.tmxdata.objects: #each object to screen
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
        self.mainMenu(1) if menu else self.run()

    def panCamera(self, speed):  
        self.panner = sprite.Panner(setting.WIDTH / 2, 0)
        y = setting.HEIGHT / 2 - 10 #panner start position
        panMessage = { "message1" : [self.font, setting.ALLTEXT["panText"] + str(self.level), 70, setting.WHITE, 180, setting.HEIGHT / 2 - 30]}
        while y < self.map.height - (setting.HEIGHT / 2):     
            self.dt = self.clock.tick(setting.FPS) / 1000
            self.panner.rect.y = y
            self.camera.update(self.panner) #make screen pan down    
            self.vehicleSprites.update()
            self.keyEvents()    
            self.draw(panMessage, True)        
            y += speed
        return       

    def mainMenu(self, speed):        
        self.lives = setting.PLAYERLIVES  
        self.score = setting.DEFAULTSCORE
        self.panner = sprite.Panner(setting.WIDTH / 2, 0)
        completeMessages = { "colorMessage" : [self.font, setting.ALLTEXT["menuText"], 70, setting.WHITE, 130, setting.HEIGHT - 104]}
        self.pos = sprite.MousePos(self, completeMessages, True)
        y = setting.HEIGHT / 2 - 10 #panner start position
        self.button1 = sprite.Obstacle(self, 100, setting.HEIGHT - 104, 600, 70)       
        while True:
            self.dt = self.clock.tick(setting.FPS) / 1000
            self.panner.rect.y = y
            self.button1.rect.y += speed
            self.camera.update(self.panner) #make screen pan down
            self.vehicleSprites.update()
            self.pos.update()
            self.keyEvents()
            y += speed
            if y >= self.map.height - (setting.HEIGHT / 2): #infinatly scroll down
                y = setting.HEIGHT / 2
                self.button1.rect.y = setting.HEIGHT - 104
            if self.pos.pressed:
                break
        self.level += 1 #to first level
        self.showInfo("data/images/gameExplain.png")
        self.showInfo("data/images/deathExplain.png")
        self.showInfo("data/images/controls.png")
        return 

    def run(self):
        self.playing = True
        self.panCamera(self.map.height / setting.PANSPEED)
        while self.playing: #gameloop
            self.keyEvents()
            self.update()          
    
    def update(self):
        self.dt = self.clock.tick(setting.FPS) / 1000     
        self.allSprites.update()        
        self.camera.update(self.player)
        now = pygame.time.get_ticks()
        self.timer -= self.dt

        hits = pygame.sprite.spritecollide(self.player, self.vehicleSprites, False, maps.collide_hit_rect)
        print(hits)
        if self.timer < 0 or hits:
            # Run out of time
            self.lives -= 1
            if self.lives < 1:
                # game over
                score = "0" if self.score <= 0 else str(round(self.score, 0))[:-2]
                gameOverMessages = { "message1" : [self.font, setting.ALLTEXT["gameOverText"][0], 70, setting.WHITE, 80, setting.TILESIZE], 
                                  "message2" : [self.font, setting.ALLTEXT["gameOverText"][1] + score, 70, setting.WHITE, 180, setting.HEIGHT / 2 - 50],
                                  "colorMessage" : [self.font, setting.ALLTEXT["gameOverText"][2], 70, setting.WHITE, 120, setting.HEIGHT - 164]}
                self.textScreen(gameOverMessages)
                self.level = setting.DEFAULTLEVEL #go back to beggining level  
                self.load(True) #reset the game
                self.load()
            else:
                self.player.image = self.playerGraveImage
                deathMessages = { "message1" : [self.font, setting.ALLTEXT["deathText"][0], 70, setting.WHITE, 140, setting.TILESIZE], 
                                  "message2" : [self.font,  setting.ALLTEXT["deathText"][1] + str(self.lives), 70, setting.WHITE, 180, setting.HEIGHT / 2 - 50],
                                  "colorMessage" : [self.font, setting.ALLTEXT["deathText"][2], 70, setting.WHITE, 180, setting.HEIGHT - 164]}
                self.textScreen(deathMessages)
                self.load()
   
        # Completes a level
        if pygame.sprite.collide_rect(self.player, self.recycleBin):
            if self.player.litter >= self.litter:
                self.level += 1
                self.score += self.timer
                if self.level > 3:
                    gameCompleteMessages = { "message1" : [self.font, setting.ALLTEXT["gameCompleteText"][0], 70, setting.WHITE, 260, setting.TILESIZE], 
                                         "message2" : [self.font, setting.ALLTEXT["gameCompleteText"][1], 70, setting.WHITE, 140, setting.TILESIZE + 100],
                                         "message3" : [self.font, setting.ALLTEXT["gameCompleteText"][2] + str(round(self.score, 0))[:-2], 70, setting.WHITE, 150, setting.HEIGHT / 2],
                                         "colorMessage" : [self.font, setting.ALLTEXT["gameCompleteText"][3], 70, setting.WHITE, 120, setting.HEIGHT - 164]}
                    self.textScreen(gameCompleteMessages)
                    self.level = setting.DEFAULTLEVEL  
                    self.load(True)
                    self.load()
                else:
                    completeMessages = { "message" : [self.font, setting.ALLTEXT["completeText"][0], 70, setting.WHITE, 240, setting.TILESIZE], 
                                         "message2" : [self.font, setting.ALLTEXT["completeText"][1], 70, setting.WHITE, 140, setting.TILESIZE + 100],
                                         "message3" : [self.font, setting.ALLTEXT["completeText"][2] + str(round(self.score, 0))[:-2], 70, setting.WHITE, 150, setting.HEIGHT / 2],
                                         "colorMessage" : [self.font, setting.ALLTEXT["completeText"][3], 70, setting.WHITE, 100, setting.HEIGHT - 164]}
                    self.textScreen(completeMessages)
                    self.load()
   
        # Collects litter
        hits = pygame.sprite.spritecollide(self.player, self.litterSprites, False)
        if hits:
            self.player.litter += 1
            self.litterSprites.remove(hits[0])
            self.allSprites.remove(hits[0])
            hits[0].kill() #remove litter from screen after groups

        percent = (self.player.litter / self.litter) * 100 #how much litter the player has obtained
        percentX = self.renderObjectImage(self.player.litter, setting.WIDTH - 74, setting.HEIGHT - 74, self.litterImages[0], -74)
        gameMessages = { "message1" : [self.font, setting.ALLTEXT["gameText"] + str(round(self.timer, 0))[:-2], 40, setting.WHITE, 270, 22], 
                         "message2" : [self.font, str(round(percent, 0))[:-2] + u"%", 40, setting.WHITE, percentX - 55, setting.HEIGHT - 65]}
        self.draw(gameMessages, False, True)

    def keyEvents(self, end = False):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN and end: #only for info screens
                    return False
        return True

    def renderMessage(self, font, text, size, colour, x, y):
        font = pygame.font.Font(font, size)
        text_surface = font.render(text, True, colour)
        text_rect = text_surface.get_rect()
        text_rect.x = x
        text_rect.y = y
        self.gameDisplay.blit(text_surface, text_rect)
        return text_rect

    def renderObjectImage(self, k, x, y, img, increment):
        for i in range(k): #repeat for the number of objects, k
            self.gameDisplay.blit(img, (x, y))
            x += increment #draw at next location
        return x

    def textScreen(self, messages):
        self.pos = sprite.MousePos(self, messages, False)
        self.button1 = sprite.Obstacle(self, 100, (setting.HEIGHT - 164) - self.camera.y, 600, 70) # - camera y to revert apply   
        while True:
            self.dt = self.clock.tick(setting.FPS) / 1000
            self.vehicleSprites.update()
            self.pos.update()    
            self.keyEvents()
            if self.pos.pressed: #when player 'presses' button
                break
        return

    def fade_screen(self, background, fade, time):
        for x in range(fade):
            self.gameDisplay.blit(background, (0, 0))
            self.fadeSurface.fill(setting.BLACK)
            self.fadeSurface.set_alpha(0 + x * time) #decrease opacity
            self.gameDisplay.blit(self.fadeSurface, (0, 0))
            self.dt = self.clock.tick(setting.FPS) / 1000
            self.keyEvents()
            pygame.display.update()

    def showInfo(self, img):
        background = pygame.image.load(img).convert_alpha()
        running = True
        while running:
            self.dt = self.clock.tick(setting.FPS) / 1000
            self.gameDisplay.blit(background, (0, 0))
            running = self.keyEvents(True) #return if the player escapes the screen
            pygame.display.update()
            if not running:
                break
        self.fade_screen(background, 50, 5) #when complete, fade screen

    def draw_grid(self):
        for x in range(0, setting.WIDTH, setting.TILESIZE):
            pygame.draw.line(self.gameDisplay, setting.YELLOW, (x, 0), (x, setting.HEIGHT))
        for y in range(0, setting.HEIGHT, setting.TILESIZE):
            pygame.draw.line(self.gameDisplay, setting.YELLOW, (0, y), (setting.WIDTH, y))

    def draw(self, messageDict = None, fadeSurf = False, game = False, menu = False):   
        self.gameDisplay.blit(self.mapImg, self.camera.apply_rect(self.mapRect))   
        self.fadeSurface.fill(setting.BLACK)
        self.fadeSurface.set_alpha(150)
    
        for s in self.allSprites:
            if not isinstance(s, sprite.Player):
                self.gameDisplay.blit(s.image, self.camera.apply(s)) #apply camera so locations are expressive      
            pygame.draw.rect(self.gameDisplay, setting.BLUE, self.camera.apply_rect(s.rect), 2)
                   
        for s in self.allSprites:
            if isinstance(s, sprite.Player):
                self.gameDisplay.blit(s.image, self.camera.apply(s))
                pygame.draw.rect(self.gameDisplay, setting.BLUE, self.camera.apply_rect(s.hit_rect), 2)

        self.draw_grid()
        if fadeSurf: self.gameDisplay.blit(self.fadeSurface, (0, 0))
        if menu: self.gameDisplay.blit(self.titleImage, (0, 0))
        if messageDict != None: #if there are messages to write
            for value in messageDict.values():
                self.renderMessage(value[0], value[1], value[2], value[3], value[4], value[5]) #draw each message

        if game:
            self.renderObjectImage(self.player.lives, 10, setting.HEIGHT - 74, self.heartImage, 74)
            self.renderObjectImage(self.player.litter, setting.WIDTH - 74, setting.HEIGHT - 74, self.litterImages[2], -74)
        pygame.display.update()

if __name__ == "__main__":
    g = Game()
    while g.running:
        g.load(False) #run the game
    pygame.quit()
    sys.exit()
