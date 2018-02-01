import pygame
import sys
import os
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
        mapFolder = os.path.join(dataFolder, "maps")
        imgFolder = os.path.join(dataFolder, "images")
        fontFoler = os.path.join(dataFolder, "fonts")
        self.font = os.path.join(fontFoler, setting.FONT)
        self.map = maps.TiledMap(os.path.join(mapFolder, "map.tmx"))
        self.mapImg = self.map.make_map()
        self.mapRect = self.mapImg.get_rect()
        self.playerImage = pygame.image.load(os.path.join(imgFolder, setting.PLAYERIMG)).convert_alpha()
        self.playerRotate = pygame.image.load(os.path.join(imgFolder, setting.PLAYERROTATE)).convert_alpha()
        self.playerFlip = pygame.image.load(os.path.join(imgFolder, setting.PLAYERFLIP)).convert_alpha()
        self.playerRotate1 = pygame.image.load(os.path.join(imgFolder, setting.PLAYERROTATE1)).convert_alpha()

    def getMap(self):
        pass

    def genMap(self):
        pass

    def load(self):
        self.allSprites = pygame.sprite.Group()
        self.litterSprites = pygame.sprite.Group()
        self.collisionSprites = pygame.sprite.Group()

        for tileObject in self.map.tmxdata.objects:
            if tileObject.name == "Player":
                self.player = sprite.Player(self, tileObject.x, tileObject.y)
            if tileObject.name == "Collision":
                sprite.Obstacle(self, tileObject.x, tileObject.y, tileObject.width, tileObject.height)

        self.camera = maps.Camera(self.map.width, self.map.height)
        self.run()

    def panCamera(self, speed):  
        self.panner = sprite.Panner(self, setting.WIDTH / 2, 0)
        y = setting.HEIGHT / 2
        while y < self.map.height - (setting.HEIGHT / 2):
            self.panner.rect.y = y
            self.camera.update(self.panner)    
            self.keyEvents()
            self.draw(True)        
            y += speed

    def run(self):
        self.playing = True
        self.panCamera(setting.PANSPEED)
        while self.playing:
           self.dt = self.clock.tick(setting.FPS) / 1000
           self.keyEvents()
           self.update()
           self.draw()

    def update(self):
        # When not panning down
        self.allSprites.update()
        self.camera.update(self.player)

    def keyEvents(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

    def render_message(self, font, text, size, colour, x, y):
        ####render a message to the screen####
        font = pygame.font.Font(font, size)
        text_surface = font.render(text, True, colour)
        text_rect = text_surface.get_rect()
        text_rect.x = x
        text_rect.y = y
        self.gameDisplay.blit(text_surface, text_rect)

    def draw(self, level = False):
        self.gameDisplay.blit(self.mapImg, self.camera.apply_rect(self.mapRect))
        for s in self.allSprites:
            self.gameDisplay.blit(s.image, self.camera.apply(s))
        if level:
            self.render_message(self.font, "LEVEL 1", 90, setting.WHITE, 250, setting.HEIGHT / 2)
        pygame.display.update()

if __name__ == "__main__":
    g = Game()
    while g.running:
        g.load()
    pygame.quit()
