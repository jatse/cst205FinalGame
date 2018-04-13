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

#------------------------
#----- PLAYER CLASS -----
#------------------------
class Player(object):
  def __init__(self, intX = 0, intY = 0):
    self.sprite = makePicture("images/player_sprite.jpg")
    self.x = intX  
    self.y = intY
  
        
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
  moveTo(renderCoord, 0 , 0)    
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
  pasteToMap(updateMap, player.sprite, player.x, player.y, white)                   #add player to updateMap   
  pasteToMap(hitMap, makeEmptyPicture(32, 32, red), player.x, player.y)          #add player to hitMap 
  
  #--- MAIN GAME LOOP ---
  while true:
    #- 1. render graphics   
    moveTo(renderCoord, 0 , 0)                                                      #move to render full screen image
    drop(renderCoord, updateMap)                                                    #output to screen
    #repaint(hitMap)                                                                 #DEBUG: show hit map
    
    #- 2. get user input
    while true:                                                                    #keep getting input until input matches valid commands    
      userInput = requestString("What would you like to do?")
      userInput.strip().lower()
      if userInput in ["n","s","e","w","north","south","east","west","r","rest"]:    
        break
        
    #- 3. execute player's turn
    #movement check. if move command in bounds and not collide with object, allow move.
    #encounter check. check if player collided with enemy or item.
    #update maps
    if userInput in ["n", "north"]:
      if player.y - 32 >= 32 and not collisionCheck(hitMap, player.sprite, player.x, player.y - 32, black):
        pasteToMap(hitMap, makeEmptyPicture(32, 32, white), player.x, player.y)  #remove from hitMap
        grassPatch(grassMap, updateMap, player.x, player.y)                      #remove from updateMap
        player.y -= 32                                                           #move
        pasteToMap(hitMap, makeEmptyPicture(32, 32, red), player.x, player.y)    #add back into hitMap
        pasteToMap(updateMap, player.sprite, player.x, player.y, white)          #add back into update Map
    elif userInput in ["s", "south"]:
      if player.y + 32 <= 512 and not collisionCheck(hitMap, player.sprite, player.x, player.y + 32, black):
        pasteToMap(hitMap, makeEmptyPicture(32, 32, white), player.x, player.y)
        grassPatch(grassMap, updateMap, player.x, player.y) 
        player.y += 32
        pasteToMap(hitMap, makeEmptyPicture(32, 32, red), player.x, player.y)
        pasteToMap(updateMap, player.sprite, player.x, player.y, white)   
    elif userInput in ["w", "west"]:
      if player.x - 32 >= 0 and not collisionCheck(hitMap, player.sprite, player.x - 32, player.y, black): 
        pasteToMap(hitMap, makeEmptyPicture(32, 32, white), player.x, player.y)
        grassPatch(grassMap, updateMap, player.x, player.y) 
        player.x -= 32
        pasteToMap(hitMap, makeEmptyPicture(32, 32, red), player.x, player.y)
        pasteToMap(updateMap, player.sprite, player.x, player.y, white)   
    elif userInput in ["e", "east"]:
      if player.x + 32 <= 778 and not collisionCheck(hitMap, player.sprite, player.x + 32, player.y, black):
        pasteToMap(hitMap, makeEmptyPicture(32, 32, white), player.x, player.y)
        grassPatch(grassMap, updateMap, player.x, player.y) 
        player.x += 32
        pasteToMap(hitMap, makeEmptyPicture(32, 32, red), player.x, player.y)
        pasteToMap(updateMap, player.sprite, player.x, player.y, white)   
      
    #axe action
    
    
    #- 4. execute enemies' turn
    
    #- 5. execute game events
    
    
      
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
  
#Checks if given object collides on hitMap and 
#return boolean true if collision detected, otherwise false
#Does not alter hitMap
#targetColor definitions:
#black = obstacles, uninteractive
#red = player's character
#blue = enemy character
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
