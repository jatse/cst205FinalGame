#Jason Tse
#CST 205 Final Project

#--- MODULE IMPORT AND MEDIA DIRECTORY
import time
import random
import thread
currentDirectory = __file__[:-13] #removes this file's name from file path to get current directory
setMediaFolder(currentDirectory)


#--- PLAYER CLASS


#--- MAIN GAME LOOP
def main():
  #loading window and tutorial
  tutorialMsg = "Work in progress ... Loading"
  thread.start_new_thread(showInformation, (tutorialMsg,))
  
  #create turtle renderer to output graphics
  renderOutput = makeWorld(800, 600)
  renderCoord = makeTurtle(renderOutput)
  renderCoord.penUp()  #stop turtle pen trail
  renderCoord.hide()   #hide turtle icon
  moveTo(renderCoord, 0 , 0)  #move to render full screen image
  
  #generate random map
  #map is 800 x 544 broken into 25 x 17 cells of 32 pixel width squares
  #map will be randomized for every game instance
  unit = 32
  rockSpawnCount = 5    #determines number of rocks spawned on map
  rockTile = makePicture(currentDirectory + "images/rock_tile.jpg")
  treeSpawnCount = 4    #determines number of trees spawned on map
  treeTile = makePicture(currentDirectory + "images/tree_tile.jpg")
  
  gameMap = makeEmptyPicture(800, 600, black)  #gameMap is the displayed graphics
  hitMap = makeEmptyPicture(800, 600, white)   #hitMap is used for collision detections
  
  #generate grass tiles
  for x in range(0, 800, unit):
    for y in range(32, 544, unit):
      #get random grass tile (5 different tiles)
      tileNum = random.randint(1, 5)
      grassTile = makePicture(currentDirectory + "images/grass_tiles" + str(tileNum) + ".jpg")
      gameMap = pasteToMap(gameMap, grassTile, x, y, 32, 32)
  #generate tree and rock obstacles
  for i in range(rockSpawnCount):
    rockX = random.randrange(0, 778, 32)
    rockY = random.randrange(32, 512, 32)
    pasteToMap(gameMap, rockTile, rockX, rockY, 32, 32)
  for i in range(treeSpawnCount):
    treeX = random.randrange(0, 778, 32)
    treeY = random.randrange(32, 480, 32)
    pasteToMap(gameMap, treeTile, treeX, treeY, 32, 64)
  
    drop(renderCoord, gameMap)
      
#--- Other functions
#Pastes a tile to the display map, and returns the updated map.
def pasteToMap(map, tile, mapX, mapY, tileWidth, tileHeight):
  tileX = 0
  tileY = 0
  for x in range(mapX, mapX+tileWidth):
    for y in range(mapY, mapY+tileHeight):
      inputPixel = getPixel(tile,tileX,tileY)
      outputPixel = getPixel(map, x, y)
      setColor(outputPixel, getColor(inputPixel))
      tileY += 1
    tileX += 1
    tileY = 0
  return map
  
#--- Execution
main()
  