#Jason Tse
#CST 205 Final Project

#---------------------------------------------
#----- MODULE IMPORT AND MEDIA DIRECTORY -----
#---------------------------------------------
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
  """
    Initialization sets up the first screen the player sees.
    The gameMap with tiles and obstacles will not change during gameplay.
    An updateMap will be used for placing sprites.
    The hitMap image will be updated to reflect the location of game elements.
  """

  #create turtle renderer to output graphics
  renderOutput = makeWorld(800, 600)
  renderCoord = makeTurtle(renderOutput)
  renderCoord.penUp()         #stop turtle pen trail
  renderCoord.hide()          #hide turtle icon
  
  #loading screen
  loadingScreen = makePicture("images/loading_screen.jpg")
  moveTo(renderCoord, 0 , 0)    
  drop(renderCoord, loadingScreen)  
  
  #generate random map
  #map is actively 800 x 544 broken into 25 x 17 cells of 32 pixel width squares
  #map will be randomized for every game instance
  gameMap = makeEmptyPicture(800, 600, black)    #gameMap is the initial game layout
  updateMap = makeEmptyPicture(800, 600)         #updateMap is the rendered image for imposing sprites
  hitMap = makeEmptyPicture(800, 600, white)     #hitMap is used for collision detections

  rockSpawnCount = 4                             #determines number of rocks spawned on map
  rockTile = makePicture("images/rock_tile.jpg")
  treeSpawnCount = 8                             #determines number of trees spawned on map
  treeTile = makePicture("images/tree_tile.jpg")
  spawnX = random.randrange(0, 778, 32)          #initial spawn point set at random
  spawnY = random.randrange(32, 512, 32)
  
  #initialize hitMap by framing active area
  for pixels in getPixels(hitMap):
    if getY(pixels) < 32 or getY(pixels) > 544:
      setColor(pixels, black)
  #generate grass tiles
  for x in range(0, 800, unit):
    for y in range(32, 544, unit):
      tileNum = random.randint(1, 5)                                             #get random grass tile (5 different tiles)
      grassTile = makePicture("images/grass_tiles" + str(tileNum) + ".jpg")
      pasteToMap(gameMap, grassTile, x, y)                                       #build base for gameMap
  #generate rock obstacles
  for i in range(rockSpawnCount):
    while collisionCheck(hitMap, rockTile, spawnX, spawnY, black):               #make sure obstacles do not overlap
      spawnX = random.randrange(0, 778, 32)
      spawnY = random.randrange(32, 512, 32)
    pasteToMap(gameMap, rockTile, spawnX, spawnY)                                #update gameMap
    pasteToMap(hitMap, makeEmptyPicture(32, 32, black), spawnX, spawnY)          #update hitMap
  #generate tree obstacles
  for i in range(treeSpawnCount):
    while collisionCheck(hitMap, treeTile, spawnX, spawnY, black): 
      spawnX = random.randrange(0, 778, 32)
      spawnY = random.randrange(32, 480, 32)
    pasteToMap(gameMap, treeTile, spawnX, spawnY)
    pasteToMap(hitMap, makeEmptyPicture(32, 64, black), spawnX, spawnY)
    
  #spawn player
  player = Player(random.randrange(0, 778, 32), random.randrange(32, 512, 32))   #creates Player object with random starting coordinates
  while collisionCheck(hitMap, player.sprite, player.x, player.y, black):        #make sure player does not start on obstacle
    player.x = random.randrange(0, 778, 32)
    player.y = random.randrange(32, 512, 32)  
  pasteToMap(hitMap, makeEmptyPicture(32, 32, red), player.x, player.y)          #add player to hitMap 
  
  cloneMap(gameMap, updateMap)                                                   #clone gameMap to updateMap in preparation for sprites 
  
  #--- MAIN GAME LOOP ---
  while true:
    #- 1. render graphics  
    pasteToMap(updateMap, player.sprite, player.x, player.y, white)                 #update player location on map   
    
    moveTo(renderCoord, 0 , 0)                                                      #move to render full screen image
    drop(renderCoord, updateMap)                                                    #output to screen
    #repaint(hitMap)                                                                 #DEBUG: show hit map
    
    #- 2. get user input
    bgThread = threading.Thread(target = cloneMap, args = (gameMap,updateMap))     #reset update map for next loop now. loop slow otherwise
    bgThread.start()
    while true:                                                                    #keep getting input until input matches valid commands
      userInput = requestString("What would you like to do?")
      userInput.strip().lower()
      if userInput in ["n","s","e","w","north","south","east","west","r","rest"]:    
        break
        
    #- 3. execute player's turn
    #movement check. if move command in bounds and not collide with object, allow move.
    #encounter check. check if player collided with enemy or item.
    #update hitMap
    if userInput in ["n", "north"]:
      if player.y - 32 >= 32 and not collisionCheck(hitMap, player.sprite, player.x, player.y - 32, black):
        pasteToMap(hitMap, makeEmptyPicture(32, 32, white), player.x, player.y)  #remove from hitMap
        player.y -= 32                                                           #move
        pasteToMap(hitMap, makeEmptyPicture(32, 32, red), player.x, player.y)    #add back into hitMap
    elif userInput in ["s", "south"]:
      if player.y + 32 <= 512 and not collisionCheck(hitMap, player.sprite, player.x, player.y + 32, black):
        pasteToMap(hitMap, makeEmptyPicture(32, 32, white), player.x, player.y)
        player.y += 32
        pasteToMap(hitMap, makeEmptyPicture(32, 32, red), player.x, player.y)
    elif userInput in ["w", "west"]:
      if player.x - 32 >= 0 and not collisionCheck(hitMap, player.sprite, player.x - 32, player.y, black): 
        pasteToMap(hitMap, makeEmptyPicture(32, 32, white), player.x, player.y)
        player.x -= 32
        pasteToMap(hitMap, makeEmptyPicture(32, 32, red), player.x, player.y)
    elif userInput in ["e", "east"]:
      if player.x + 32 <= 778 and not collisionCheck(hitMap, player.sprite, player.x + 32, player.y, black):
        pasteToMap(hitMap, makeEmptyPicture(32, 32, white), player.x, player.y)
        player.x += 32
        pasteToMap(hitMap, makeEmptyPicture(32, 32, red), player.x, player.y)
      
    #axe action
    
    
    #- 4. execute enemies' turn
    
    #- 5. execute game events
    bgThread.join()   #make sure updateMap is completely reset. otherwise artifacts may appear.
      
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
  for pixels in getPixels(copyFromMap):
    outputPixel = getPixel(copyToMap, getX(pixels), getY(pixels))
    setColor(outputPixel, getColor(pixels))
 
  
#-------------------------  
#----- FUNCTION CALL -----
#-------------------------
main()
  