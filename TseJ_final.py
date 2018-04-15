#Jason Tse
#CST 205 Final Project

#-------------------------------------------------
#----- MODULE IMPORT AND SET MEDIA DIRECTORY -----
#-------------------------------------------------
import time       #imported for animations
import random     #imported for random generation of game elements
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
    #remove sprite from map
    pasteToMap(hitMap, makeEmptyPicture(32, 32, white), self.x, self.y)
    grassPatch(grassMap, updateMap, self.x, self.y)
    #move coordinates 
    self.x += xDelta
    self.y += yDelta
    #render new coordinates
    pasteToMap(hitMap, makeEmptyPicture(32, 32, self.color), self.x, self.y)
    pasteToMap(updateMap, self.sprite, self.x, self.y, white) 
  
  #returns coordinate of somewhere closer to the prey, if not obstructed
  def hunt(self, prey, hitMap):
    clearN = false
    clearS = false
    clearE = false
    clearW = false
    
    #checks if cardinal directions are available
    if self.x - 32 > 0 and (collisionCheck(hitMap, self.sprite, self.x - 32, self.y, white) or collisionCheck(hitMap, self.sprite, self.x - 32, self.y, red)):
      clearW = true
    if self.x + 32 < 768 and (collisionCheck(hitMap, self.sprite, self.x + 32, self.y, white) or collisionCheck(hitMap, self.sprite, self.x + 32, self.y, red)):
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
    self.axeCount = 5
    
  #overridden to allow item pickup
  def move(self, updateMap, hitMap, grassMap, xDelta, yDelta, axesOnScreen):
    #remove sprite from map
    pasteToMap(hitMap, makeEmptyPicture(32, 32, white), self.x, self.y)
    grassPatch(grassMap, updateMap, self.x, self.y)
    #move coordinates 
    self.x += xDelta
    self.y += yDelta
    #if axe there, pick it up
    if collisionCheck(hitMap, self.sprite, self.x, self.y, green):
      self.axeCount += 1
      axesOnScreen -= 1
    #if you walked into enemy, return for check for gameover
    if collisionCheck(hitMap, self.sprite, self.x, self.y, blue):
      return axesOnScreen
    #render new coordinates
    pasteToMap(hitMap, makeEmptyPicture(32, 32, self.color), self.x, self.y)
    pasteToMap(updateMap, self.sprite, self.x, self.y, white) 
    #return count of axes on screen
    return axesOnScreen
    
  def throwAxe(self, enemies, enemyCount, updateMap, hitMap, grassMap, xDelta, yDelta, renderCoord):
    #use axe
    self.axeCount -= 1
    currentAxeSprite = 1
    play(makeSound("audio/axe_throw.wav"))
    #throw up to 5 spaces
    for i in range(5):
      xDistance = self.x + (xDelta * (i + 1))
      yDistance = self.y + (yDelta * (i + 1))
      #if beyond bounds, stop throw.
      if xDistance > 768 or xDistance < 0 or yDistance < 32 or yDistance > 512:
        return enemyCount
      #if not an obstacle, paste axe in direction. farther with each loop.
      if not collisionCheck(hitMap, self.sprite, xDistance, yDistance, black):
        #then paste axe there and render. if item there, skip render and check.
        if not collisionCheck(hitMap, self.sprite, xDistance, yDistance, green):
          pasteToMap(updateMap, makePicture("images/axe_sprite" + str(currentAxeSprite) + ".jpg"), xDistance, yDistance, white)
          drop(renderCoord, updateMap)
          time.sleep(.5)  #slow down for visible animation
          #check if enemy was hit
          if collisionCheck(hitMap, self.sprite, xDistance, yDistance, blue):
            #if so, find which enemy was hit
            for i in range(enemyCount):
              if enemies[i].x == xDistance and enemies[i].y == yDistance:
                #decrease their hp by 1
                enemies[i].hp -= 1
                #wipe enemy from maps if no hp
                if enemies[i].hp == 0:
                  if enemies[i].nameType == "wolf": 
                    play(makeSound("audio/wolf_ko.wav"))
                  else:
                    play(makeSound("audio/bear_ko.wav"))
                  pasteToMap(hitMap, makeEmptyPicture(32, 32, white), xDistance, yDistance)
                  grassPatch(grassMap, updateMap, xDistance, yDistance)
                  drop(renderCoord, updateMap)
                  #remove from enemy list, update count variable, and stop throw
                  del enemies[i]
                  return enemyCount - 1;
                #else enemy still has hp, no wipe but end throw
                else:
                  play(makeSound("audio/bear_hit.wav"))
                  return enemyCount
          else: #if no enemy was hit, remove axe
            grassPatch(grassMap, updateMap, xDistance, yDistance)
            drop(renderCoord, updateMap)
          #rotate axe sprite
          if currentAxeSprite == 3:
            currentAxeSprite = 1
          else:
            currentAxeSprite += 1
          play(makeSound("audio/axe_fly.wav"))
      else:
        return enemyCount  #if obstacle encountered, end throw.
    
class Wolf(Sprite):
  def __init__(self, intX = 0, intY = 0):
    Sprite.__init__(self, intX, intY)
    self.sprite = makePicture("images/wolf_sprite.jpg")
    self.nameType = "wolf"
    self.color = blue
    self.hp = 1
  
  #wolf will wander 10% of the time   
  def wander(self, prey, hitMap):
    clearN = false
    clearS = false
    clearE = false
    clearW = false
    
    #checks if cardinal directions are available
    if self.x - 32 > 0 and (collisionCheck(hitMap, self.sprite, self.x - 32, self.y, white) or collisionCheck(hitMap, self.sprite, self.x - 32, self.y, red)):
      clearW = true
    if self.x + 32 < 768 and (collisionCheck(hitMap, self.sprite, self.x + 32, self.y, white) or collisionCheck(hitMap, self.sprite, self.x + 32, self.y, red)):
      clearE = true
    if self.y - 32 > 32 and (collisionCheck(hitMap, self.sprite, self.x, self.y - 32, white) or collisionCheck(hitMap, self.sprite, self.x, self.y - 32, red)):
      clearN = true
    if self.y + 32 < 512 and (collisionCheck(hitMap, self.sprite, self.x, self.y + 32, white) or collisionCheck(hitMap, self.sprite, self.x, self.y + 32, red)):
      clearS = true
      
    #if surrounded by obstacles, stay
    if clearN == false and clearE == false and clearS == false and clearW == false:
      return 0, 0
      
    #else, go in random direction  
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
  
class Bear(Sprite):
  def __init__(self, intX = 0, intY = 0):
    Sprite.__init__(self, intX, intY)
    self.sprite = makePicture("images/bear_sprite.jpg")
    self.nameType = "bear"
    self.color = blue
    self.hp = 3
        
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
  grassMap = makeEmptyPicture(800, 600, black)   #underlying map of grass.
  updateMap = makePicture("images/map-help.jpg") #the map to be displayed
  hitMap = makeEmptyPicture(800, 600, white)     #map used for collision detections
  
  rockSpawnCount = 6                             #determines number of rocks spawned on map
  rockTile = makePicture("images/rock_tile.jpg")
  treeSpawnCount = 13                             #determines number of trees spawned on map
  treeTile = makePicture("images/tree_tile.jpg")
  
  #initialize hitMap by framing active area with obstacles
  for pixels in getPixels(hitMap):
    if getY(pixels) < 32 or getY(pixels) > 544:
      setColor(pixels, black)
      
  #generate grass tiles
  for x in range(0, 800, 32):
    for y in range(32, 544, 32):
      tileNum = random.randint(1, 5)                                             #get random grass tile number (5 different tiles)
      grassTile = makePicture("images/grass_tiles" + str(tileNum) + ".jpg")   
      pasteToMap(grassMap, grassTile, x, y)                                      #build grassMap
      pasteToMap(updateMap, grassTile, x, y)                                     #initialize update map
  #generate rock obstacles
  for i in range(rockSpawnCount):
    spawnRandom(updateMap, hitMap, rockTile, black)
  #generate tree obstacles
  for i in range(treeSpawnCount):
    spawnRandom(updateMap, hitMap, treeTile, black)
    
  #spawn player
  player = Player()
  spawnRandomMoveable(updateMap, hitMap, player, red, white)
  
  #spawn 3 starting wolves
  enemies = []                                                        #holds enemy objects
  enemyCount = 0
  for i in range(3):
    enemies.append(Wolf())                                            #adds new wolf to enemy list
    spawnRandomMoveable(updateMap, hitMap, enemies[i], blue, white)
    enemyCount += 1
    
  #prepare axe UI graphics
  uiAxe = makePicture("images/axe_sprite1.jpg")
  noAxe = makeEmptyPicture(32, 32, black)
  axesOnScreen = 0
  
  #--- MAIN GAME LOOP ---
  turnCount = 1   #used to trigger in game events
  
  while true:
    #- 1. update UI and render graphics 
    for i in range(10):                                               #refresh axe count UI
      if player.axeCount > i:
        pasteToMap(updateMap, uiAxe, 32 * i, 0, white)
      else: 
        pasteToMap(updateMap, noAxe, 32 * i, 0, white)
        
    drop(renderCoord, updateMap)                                      #output to screen
    #repaint(hitMap)                                                  #DEBUG: show hit map
    
    #- 2. get user input
    while true:                                                       #keep getting input until input matches valid commands    
      userInput = requestString("What would you like to do?")
      userInput.strip().lower()
      if userInput in ["n","s","e","w","north","south","east","west","r","rest","a","axe"]:    
        break
        
    #- 3. execute player's turn
    successfulTurn = false  #if player runs into obstacle or doesn't throw axe, turn does not count
    
    #movement check. if move command in bounds and space is free, then allow move
    if userInput in ["n", "north"]:
      if player.y - 32 >= 32 and not collisionCheck(hitMap, player.sprite, player.x, player.y - 32, black):
        axesOnScreen = player.move(updateMap, hitMap, grassMap, 0, -32, axesOnScreen)
        successfulTurn = true
    elif userInput in ["s", "south"]:
      if player.y + 32 <= 512 and not collisionCheck(hitMap, player.sprite, player.x, player.y + 32, black):
        axesOnScreen = player.move(updateMap, hitMap, grassMap, 0, 32, axesOnScreen)
        successfulTurn = true   
    elif userInput in ["w", "west"]:
      if player.x - 32 >= 0 and not collisionCheck(hitMap, player.sprite, player.x - 32, player.y, black): 
        axesOnScreen = player.move(updateMap, hitMap, grassMap, -32, 0, axesOnScreen)
        successfulTurn = true    
    elif userInput in ["e", "east"]:
      if player.x + 32 <= 768 and not collisionCheck(hitMap, player.sprite, player.x + 32, player.y, black):
        axesOnScreen = player.move(updateMap, hitMap, grassMap, 32, 0, axesOnScreen)
        successfulTurn = true 
    elif userInput in ["r", "rest"]:
        successfulTurn = true   
    
    #check if player walked into enemy.
    if collisionCheck(hitMap, player.sprite, player.x, player.y, blue):    #check if player eaten
        break
                    
    #axe action
    if userInput in ["a", "axe"] and player.axeCount > 0:
      #get direction in which to throw axe
      #axe will go 5 units out
      throwDirection = requestString("Which way will you throw?")
      if throwDirection in ["n", "north"]:
        enemyCount = player.throwAxe(enemies, enemyCount, updateMap, hitMap, grassMap, 0, -32, renderCoord)
        successfulTurn = true 
      elif throwDirection in ["s", "south"]:
        enemyCount = player.throwAxe(enemies, enemyCount, updateMap, hitMap, grassMap, 0, 32, renderCoord)
        successfulTurn = true 
      elif throwDirection in ["w", "west"]:
        enemyCount = player.throwAxe(enemies, enemyCount, updateMap, hitMap, grassMap, -32, 0, renderCoord)
        successfulTurn = true 
      elif throwDirection in ["e", "east"]:
        enemyCount = player.throwAxe(enemies, enemyCount, updateMap, hitMap, grassMap, 32, 0, renderCoord)
        successfulTurn = true 
          
    #- 4. execute enemies' turn
    if successfulTurn:
      for enemy in enemies:
        if enemy.nameType == "wolf" and random.randint(0,4) == 0:            #wolves will wander 20% of the time, bears don't
          huntX, huntY = enemy.wander(player, hitMap)
        else:
          huntX, huntY = enemy.hunt(player, hitMap)                          #get where enemy should move
        enemy.move(updateMap, hitMap, grassMap, huntX, huntY)                #move
      
      if collisionCheck(hitMap, player.sprite, player.x, player.y, blue):    #check if player eaten
        break

    #- 5. execute game events
    if successfulTurn:
      #every 3 turns, try spawn to something
      if turnCount % 3 == 0:
        choice = random.randint(1,100)
        if choice > 29: #70% chance: spawn axe
          if axesOnScreen + player.axeCount < 10: #no more than 10 axes allowed (on map + in inventory)
            spawnRandom(updateMap, hitMap, uiAxe, green, white)
            axesOnScreen += 1
        elif choice > 4: #normally 25% chance: spawn wolf
          if enemyCount < 10: #maximum 10 enemies at a time
            enemies.append(Wolf())
            spawnRandomMoveable(updateMap, hitMap, enemies[len(enemies)-1], blue, white)
            play(makeSound("audio/wolf_spawn.wav"))
            enemyCount += 1 
        elif choice > 0: #normally 5% chance: spawn bear
          if enemyCount < 10: #maximum 10 enemies at a time
            enemies.append(Bear())  
            spawnRandomMoveable(updateMap, hitMap, enemies[len(enemies)-1], blue, white)
            play(makeSound("audio/bear_spawn.wav"))
            enemyCount += 1
      
      #increment turn
      turnCount += 1
  
  #--- GAME OVER ---
  gameOverScreen = makePicture("images/game_over.jpg")    
  drop(renderCoord, gameOverScreen)
  
      
#-----------------------------      
#----- MAPPING FUNCTIONS -----
#-----------------------------
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
  for xLoc in range(x, x + 32):
    for yLoc in range(y, y + 32):
      inputPixel = getPixel(grassMap, xLoc, yLoc)
      outputPixel = getPixel(updateMap, xLoc, yLoc)
      setColor(outputPixel, getColor(inputPixel))
  
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

#spawns tiles onto maps at random location   
def spawnRandom(updateMap, hitMap, tileImage, hitColor, chromaKey = 0):
  #initialize random coordinates
  spawnX = random.randrange(0, 800 - getWidth(tileImage), 32)
  spawnY = random.randrange(32, 512 - getHeight(tileImage), 32)
  #if obstructed, randomize coordinates again. trees need full check for obstacles
  while not collisionCheck(hitMap, tileImage, spawnX, spawnY, white) or collisionCheck(hitMap, tileImage, spawnX, spawnY, black):
    spawnX = random.randrange(0, 800 - getWidth(tileImage), 32)
    spawnY = random.randrange(32, 512 - getHeight(tileImage), 32)
  #paste tiles to maps
  pasteToMap(updateMap, tileImage, spawnX, spawnY, chromaKey)
  pasteToMap(hitMap, makeEmptyPicture(getWidth(tileImage), getHeight(tileImage), hitColor), spawnX, spawnY)
    
    
#spawns moveable sprites to random location 
def spawnRandomMoveable(updateMap, hitMap, moveableSprite, hitColor, chromaKey = 0):
  spriteImage = moveableSprite.sprite
  #initialize random coordinates
  spawnX = random.randrange(0, 800 - getWidth(spriteImage), 32)
  spawnY = random.randrange(32, 512 - getHeight(spriteImage), 32)
  #if obstructed, randomize coordinates again
  while not collisionCheck(hitMap, spriteImage, spawnX, spawnY, white):
    spawnX = random.randrange(0, 800 - getWidth(spriteImage), 32)
    spawnY = random.randrange(32, 512 - getHeight(spriteImage), 32)
  #assign coordinates to sprite object
  moveableSprite.x = spawnX
  moveableSprite.y = spawnY
  #paste tiles to maps
  pasteToMap(updateMap, spriteImage, spawnX, spawnY, chromaKey)
  pasteToMap(hitMap, makeEmptyPicture(getWidth(spriteImage), getHeight(spriteImage), hitColor), spawnX, spawnY)
    
    
#-------------------------  
#----- FUNCTION CALL -----
#-------------------------
main()
