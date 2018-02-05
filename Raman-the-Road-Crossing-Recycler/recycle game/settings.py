import pygame
pygame.init()

WIDTH = 768
HEIGHT = 832
TILESIZE = 64
FPS = 60
TITLE = "Raman the Road Crossing Recycler"
ICON = "logo.png"
FONT = "joystix monospace.ttf"
DEFAULTLEVEL = 0
DEFAULTSCORE = 0
RECYCLEBIN = "recycle bin.png"
TIME = 40
HEART = "heart.png"
HAZARD = "warning.png"
GRAVE = "grave.png"
TITLEIMG = "title.png"

# Litter
LITTER = "litter.png"
LITTER1 = "litter1.png"

# Vehicles
CAR = "car.png"
CAR1 = "car1.png"

# Colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 216, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LIGHTBLUE = (0, 155, 155)
GREY = (128, 128, 128)
DARKGREEN = (0, 102, 0)
BROWN = (106, 55, 5)
NIGHT_COLOR = (20, 20, 20)

# Player settings
PLAYERIMG = "player.png"
PLAYERROTATE = "player2.png"
PLAYERROTATE1 = "player4.png"
PLAYERFLIP = "player3.png"

# Values
PLAYERSPEED = 500
PLAYERFRICTION = -2
PLAYERINITIALACC = 0.5
PLAYERLIVES = 3

# Panner
PANSPEED = 500


# Messages
ALLTEXT = { "panText" : "LEVEL ",
            "gameText" : "TIME ",
            "completeText" : ["LEVEL", "COMPLETE!", "SCORE ", "NEXT LEVEL"],
            "deathText" : ["YOU DIED!", "LIVES ", "RESTART"],
            "menuText" : "PLAY GAME"}