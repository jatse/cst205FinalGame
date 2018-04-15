#Jason Tse
#CST 205 Final Project

#-------------------------------------------------
#----- MODULE IMPORT AND SET MEDIA DIRECTORY -----
#-------------------------------------------------
import time       #imported for animations
import random     #imported for random generation of game elements
import threading  #imported for running concurrent events
currentDirectory = __file__[:-13] #removes this file's name from file path to get current directory
setMediaFolder(currentDirectory)

#-----------------------------
#----- CHARACTER CLASSES -----
#-----------------------------

class Sprite(object):
  def __init__(self, intX = 0, intY = 0):
    self.x = intX  
    self.y = intY
    self.sprite = ""
    self.color = black
  
  #moves sprite
  def move(self, updateMap, hitMap, grassMap, xDelta, yDelta):
    pasteToMap(hitMap, makeEmptyPicture(32, 32, white), self.x, self.y)
    grassPatch(grassMap, updateMap, self.x, self.y) 
    self.x += xDelta
    self.y += yDelta
    pasteToMap(hitMap, makeEmptyPicture(32, 32, self.color), self.x, self.y)
    pasteToMap(updateMap, self.sprite, self.x, self.y, white) 
  
  #returns coordinate of somewhere closer to the prey, if not obstructed
  def hunt(self, prey, hitMap):
    coordX = 0
    coordY = 0 
    clearN = false
    clearS = false
    clearE = false
    clearW = false
    
    #checks if cardinal directions are available
    if self.x - 32 > 0 and (collisionCheck(hitMap, self.sprite, self.x - 32, self.y, white) or collisionCheck(hitMap, self.sprite, self.x - 32, self.y, red)):
      clearW = true
    if self.x + 32 < 778 and (collisionCheck(hitMap, self.sprite, self.x + 32, self.y, white) or collisionCheck(hitMap, self.sprite, self.x + 32, self.y, red)):
      clearE = true
    if self.y - 32 > 32 and (collisionCheck(hitMap, self.sprite, self.x, self.y - 32, white) or collisionCheck(hitMap, self.sprite, self.x, self.y - 32, red)):
      clearN = true
    if self.y + 32 < 512 and (collisionCheck(hitMap, self.sprite, self.x, self.y + 32, white) or collisionCheck(hitMap, self.sprite, self.x, self.y + 32, red)):
      clearS = true
    
    #if surrounded by obstacles, stay
    if clearN == false and clearE == false and clearS == false and clearW == false:
      return 0, 0
    
    #try moving closer
    if self.x > prey.x and clearW:
      return -32 , 0
    elif self.x < prey.x and clearE:
      return 32 , 0
    elif self.y > prey.y and clearN:
      return 0 , -32
    elif self.y < prey.y and clearS:
      return 0 , 32
    else: #if not possible, go in random available direction
      while true:
        lottery = random.randint(1,4)
        if lottery == 1 and clearW:
          return -32 , 0
        elif lottery == 2 and clearE:
          return 32 , 0
        elif lottery == 3 and clearN:
          return 0 , -32
        elif lottery == 4 and clearS:
          return 0 , 32

class Player(Sprite):
  def __init__(self, intX = 0, intY = 0):
    Sprite.__init__(self, intX, intY)
    self.sprite = makePicture("images/player_sprite.jpg")
    self.color = red
    
class Wolf(Sprite):
  def __init__(self, intX = 0, intY = 0):
    Sprite.__init__(self, intX, intY)
    self.sprite = makePicture("images/wolf_sprite.jpg")
    self.color = blue
  
class Bear(Sprite):
  def __init__(self, intX = 0, intY = 0):
    Sprite.__init__(self, intX, intY)
    self.sprite = makePicture("images/bear_sprite.jpg")
    self.color = blue
        
#--------------------------
#----- MAIN GAME LOOP -----
#--------------------------
def main():
  #--- INITIALIZATION ---
  #Initialization sets up the first screen the player sees.
  
  #create turtle renderer to output graphics
  renderOutput = makeWorld(800, 600)
  renderCoord = makeTurtle(renderOutput)
  renderCoord.penUp()         #stop turtle pen trail
  renderCoord.hide()          #hide turtle icon
  
  #output loading screen
  loadingScreen = makePicture("images/loading_screen.jpg")
  moveTo(renderCoord, 0 , 0)    #move to top left corner
  drop(renderCoord, loadingScreen)
   
  #generate random map
  #map is actively 800 x 512 broken into 25 x 16 cells of 32 pixel width squares
  #map will be randomized at start of every game
  grassMap = [[0] * 16]*25                       #underlying map of grass. grassMap[x][y]
  updateMap = makePicture("images/map-help.jpg") #the map to be displayed
  hitMap = makeEmptyPicture(800, 600, white)     #map used for collision detections
  
  rockSpawnCount = 4                             #determines number of rocks spawned on map
  rockTile = makePicture("images/rock_tile.jpg")
  treeSpawnCount = 8                             #determines number of trees spawned on map
  treeTile = makePicture("images/tree_tile.jpg")
  spawnX = random.randrange(0, 778, 32)          #initial spawn point set at random
  spawnY = random.randrange(32, 512, 32)
  
  #initialize hitMap by framing active area with obstacles
  for pixels in getPixels(hitMap):
    if getY(pixels) < 32 or getY(pixels) > 544:
      setColor(pixels, black)
      
  #generate grass tiles
  for x in range(25):
    for y in range(16):
      tileNum = random.randint(1, 5)                                             #get random grass tile (5 different tiles)
      grassTile = makePicture("images/grass_tiles" + str(tileNum) + ".jpg")
      grassMap[x][y] = grassTile                                                 #store to 2D array
      pasteToMap(updateMap, grassTile, x * 32, y * 32 + 32, chromaKey = 0)       #add to updateMap
  #generate rock obstacles
  for i in range(rockSpawnCount):
    while collisionCheck(hitMap, rockTile, spawnX, spawnY, black):               #make sure obstacles do not overlap
      spawnX = random.randrange(0, 778, 32)
      spawnY = random.randrange(32, 512, 32)
    pasteToMap(updateMap, rockTile, spawnX, spawnY)                              #add to updateMap
    pasteToMap(hitMap, makeEmptyPicture(32, 32, black), spawnX, spawnY)          #add to hitMap
  #generate tree obstacles
  for i in range(treeSpawnCount):
    while collisionCheck(hitMap, treeTile, spawnX, spawnY, black): 
      spawnX = random.randrange(0, 778, 32)
      spawnY = random.randrange(32, 480, 32)
    pasteToMap(updateMap, treeTile, spawnX, spawnY)
    pasteToMap(hitMap, makeEmptyPicture(32, 64, black), spawnX, spawnY)
    
  #spawn player
  player = Player(random.randrange(0, 778, 32), random.randrange(32, 512, 32))   #creates Player object with random starting coordinates
  while collisionCheck(hitMap, player.sprite, player.x, player.y, black):        #make sure player does not start on obstacle
    player.x = random.randrange(0, 778, 32)
    player.y = random.randrange(32, 512, 32)
  player.move(updateMap, hitMap, grassMap, 0, 0)                                 #add player to maps
  
  #spawn 3 starting wolves
  enemies = []                                                                                                #holds enemy objects (max 10)
  enemyCount = 0
  for i in range(3):
    enemies.append(Wolf(random.randrange(0, 778, 32), random.randrange(32, 512, 32)))                            #creates wolf object with random starting coordinates
    while not collisionCheck(hitMap, enemies[i].sprite, enemies[i].x, enemies[i].y, white):                   #make sure wolf is on empty space
      enemies[i].x = random.randrange(0, 778, 32)
      enemies[i].y = random.randrange(32, 512, 32)
    enemies[i].move(updateMap, hitMap, grassMap, 0, 0)                                                        #add wolf to map
    enemyCount += 1
  
  #--- MAIN GAME LOOP ---
  turnCount = 0   #used to trigger in game events
  
  while true:
    #- 1. render graphics   
    drop(renderCoord, updateMap)                                                    #output to screen
    #repaint(hitMap)                                                                 #DEBUG: show hit map
    
    #- 2. get user input
    while true:                                                                    #keep getting input until input matches valid commands    
      userInput = requestString("What would you like to do?")
      userInput.strip().lower()
      if userInput in ["n","s","e","w","north","south","east","west","r","rest"]:    
        break
        
    #- 3. execute player's turn
    successfulMove = false  #if player runs into obstacle, turn does not count
    
    #movement check. if move command in bounds and space is free, then allow move
    if userInput in ["n", "north"]:
      if player.y - 32 >= 32 and collisionCheck(hitMap, player.sprite, player.x, player.y - 32, white):
        player.move(updateMap, hitMap, grassMap, 0, -32)
        successfulMove = true
    elif userInput in ["s", "south"]:
      if player.y + 32 <= 512 and collisionCheck(hitMap, player.sprite, player.x, player.y + 32, white):
        player.move(updateMap, hitMap, grassMap, 0, 32)
        successfulMove = true   
    elif userInput in ["w", "west"]:
      if player.x - 32 >= 0 and collisionCheck(hitMap, player.sprite, player.x - 32, player.y, white): 
        player.move(updateMap, hitMap, grassMap, -32, 0)
        successfulMove = true    
    elif userInput in ["e", "east"]:
      if player.x + 32 <= 778 and collisionCheck(hitMap, player.sprite, player.x + 32, player.y, white):
        player.move(updateMap, hitMap, grassMap, 32, 0)
        successfulMove = true 
    elif userInput in ["r", "rest"]:
        successfulMove = true   
        
    #axe action
    
    
    #- 4. execute enemies' turn
    for i in range(enemyCount):
      huntX, huntY = enemies[i].hunt(player, hitMap)                #get where enemy should move
      enemies[i].move(updateMap, hitMap, grassMap, huntX, huntY)    #move
      
    if collisionCheck(hitMap, player.sprite, player.x, player.y, blue):    #check if player eaten
      break
    
    #- 5. execute game events
    turnCount += 1
  
  #--- GAME OVER ---
  gameOverScreen = makePicture("images/game_over.jpg")    
  drop(renderCoord, gameOverScreen)
  showInformation("Press OK to restart.")
  
      
#---------------------------      
#----- OTHER FUNCTIONS -----
#---------------------------
#Pastes a tile or sprite to given map.
#If chromaKey color is passed, will only copy pixels not the same as chromaKey.
def pasteToMap(map, tile, mapX, mapY, chromaKey = 0):        #chromakey is an optional parameter that will default to 0
  tileX = 0                                                     
  tileY = 0
  for x in range(mapX, mapX + getWidth(tile)):
    for y in range(mapY, mapY + getHeight(tile)):
      inputPixel = getPixel(tile,tileX,tileY)
      outputPixel = getPixel(map, x, y)
      if type(chromaKey) is not int:                         #if chromaKey is defined, only copy pixels not similar to chromaKey
        if distance(getColor(inputPixel), chromaKey) > 60:
          setColor(outputPixel, getColor(inputPixel))
      else:                                                  #else chromaKey isn't defined, copy all pixels.
        setColor(outputPixel, getColor(inputPixel))
      tileY += 1
      
    tileX += 1
    tileY = 0

#covers area with appropriate grass tile from 2D array
def grassPatch(grassMap, updateMap, x, y):
  grassTile = grassMap[x / 32][(y - 32) / 32]
  tileX = 0
  tileY = 0
  for xLoc in range(x, x + 32):
    for yLoc in range(y, y + 32):
      inputPixel = getPixel(grassTile, tileX, tileY)
      outputPixel = getPixel(updateMap, xLoc, yLoc)
      setColor(outputPixel, getColor(inputPixel))
      tileY += 1
    tileX += 1
    tileY = 0
  
#Checks for target color at object sized location at point (objectX, objectY)
#return boolean true if collision detected, otherwise false
#Does not alter hitMap
#targetColor definitions:
#black = obstacles
#red = player's character
#blue = enemies
#green = item
def collisionCheck(hitMap, object, objectX, objectY, targetColor):
  for x in range(objectX, objectX + getWidth(object)):
    for y in range(objectY, objectY + getHeight(object)):
      pixel = getPixel(hitMap, x, y)  
      if getColor(pixel) == targetColor:
        return true
  return false
  
#clones map to map
def cloneMap(copyFromMap, copyToMap):
  for x in range(0, 800):
    for y in range(0, 544):
      inputPixel = getPixel(copyFromMap, x, y)
      outputPixel = getPixel(copyToMap, x, y)
      setColor(outputPixel, getColor(inputPixel))
  
  
#-------------------------  
#----- FUNCTION CALL -----
#-------------------------
main()
