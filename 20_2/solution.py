#!/bin/python3

DEBUG = False

import enum

class Edge(enum.Enum):
  RIGHT = 1,
  LEFT = 2,
  UPPER = 3,
  LOWER = 4

class Orientation(enum.Enum):
  REGULAR = 1,
  FLIPPED_VERTICALLY = 2,
  FLIPPED_HORIZONTALLY = 3,
  FLIPPED_ALL = 4,
  UNKNOWN = 5,

class Rotation(enum.Enum):
  REGULAR = 1,
  DEG90 = 2,
  DEG180 = 3,
  DEG270 = 4,
  UNKNOWN = 5

all_orientations = [Orientation.REGULAR, Orientation.FLIPPED_HORIZONTALLY, Orientation.FLIPPED_VERTICALLY, Orientation.FLIPPED_ALL]
all_rotations = [Rotation.REGULAR, Rotation.DEG90, Rotation.DEG180, Rotation.DEG270]
all_directions = [Edge.UPPER, Edge.RIGHT, Edge.LOWER, Edge.LEFT]

monster_template = [
  "                  # ",
  "#    ##    ##    ###",
  " #  #  #  #  #  #   "
]

class ContentManipulator:
  def rotateContent90Degrees(self, content):
    rotatedContent = []
    contentLengthY = len(content)
    contentLengthX = len(content[0])
    i = 0
    while i < contentLengthX:
      rotatedContent.append("")
      i += 1

    i = 0
    while i < contentLengthX:
      j = 1
      while j <= contentLengthY:
        itemToAppend = content[contentLengthY-j][i]
        rotatedContent[i] += itemToAppend
        j += 1
      i += 1

    return rotatedContent

  def transformContentForOrientation(self, content, orientation, rotation):
    newContent = content.copy()

    # first rotate
    if rotation == Rotation.DEG90 or rotation == Rotation.DEG180 or rotation == Rotation.DEG270:
      newContent = self.rotateContent90Degrees(newContent)
    if rotation == Rotation.DEG180 or rotation == Rotation.DEG270:
      newContent = self.rotateContent90Degrees(newContent)
    if rotation == Rotation.DEG270:
      newContent = self.rotateContent90Degrees(newContent)

    # now flip horizontally
    if orientation == Orientation.FLIPPED_HORIZONTALLY or orientation == Orientation.FLIPPED_ALL:
      newNewContent = []
      for line in newContent:
        newNewContent.insert(0, line)
      newContent = newNewContent

    # now flip horizontally
    if orientation == Orientation.FLIPPED_VERTICALLY or orientation == Orientation.FLIPPED_ALL:
      i = 0
      while i < len(newContent):
        line = newContent[i]
        newLine = ""
        for char in line:
          newLine = char + newLine
        newContent[i] = newLine
        i += 1

    return newContent

  def selectEdge(self, content, direction):
    if direction == Edge.UPPER:
      return content[0]
    
    if direction == Edge.LOWER:
      return content[len(content)-1]

    if direction == Edge.LEFT:
      selectionIndex = 0
    elif direction == Edge.RIGHT:
      selectionIndex = len(content)-1
    else:
      raise NotImplementedError()

    edge = ""
    for line in content:
      edge += line[selectionIndex]
    return edge

  def getTransformedEdge(self, content, direction, orientation, rotation):
    orientedContent = self.transformContentForOrientation(content, orientation, rotation)
    return self.selectEdge(orientedContent, direction)

contentManipulator = ContentManipulator()

class Tile:
  def __init__(self, textualRepresentation):
    self.textualRepresentation = textualRepresentation
    self.initialize()
    self.orientation = Orientation.UNKNOWN
    self.rotation = Rotation.UNKNOWN
    self.contents = self.textualRepresentation.copy()
    del self.contents[0]    

  def initialize(self):
    text = self.textualRepresentation.copy()

    # get tile title
    titleLine = text.pop(0)
    self.title = int(titleLine.split("Tile ")[1].split(":")[0])

    # get tile upper edge in binary representation - left to right
    upperEdge = text[0]

    # get tile lower edge in binary representation - left to right
    lowerEdge = text[len(text)-1]

    # get tile left edge in binary representation - top to bottom
    leftEdge = ""
    for line in text:
      leftEdge+=line[0]

    # get tile right edge in binary representation - top to bottom
    rightEdge = ""
    for line in text:
      rightEdge+=line[len(line)-1]

  def setState(self, orientation, rotation):
    self.orientation = orientation
    self.rotation = rotation

  def hasState(self):
    return self.orientation != Orientation.UNKNOWN and self.rotation != Rotation.UNKNOWN

  def getEdge(self, direction):
    if self.orientation == Orientation.UNKNOWN or self.rotation == Rotation.UNKNOWN:
      raise NotImplementedError()
    return contentManipulator.getTransformedEdge(self.contents, direction, self.orientation, self.rotation)

class OrientedTile:
  def __init__(self, tile):
    if not tile.hasState():
      raise NotImplementedError()
    self.contents = contentManipulator.transformContentForOrientation(tile.contents, tile.orientation, tile.rotation)
    self.title = tile.title
    self.removeBorder()

  def removeBorder(self):
    contentLength = len(self.contents)
    del self.contents[contentLength-1]
    del self.contents[0]
    i = len(self.contents)-1
    while i >= 0:
      line = self.contents[i]
      line = line[1:contentLength-1]
      self.contents[i] = line
      i -= 1

class TileExplorer:
  def __init__(self, tiles):
    self.startTile = tiles[3]
    self.tiles = tiles
    self.checkpoint = self.startTile
    self.currentTile = self.startTile
    self.startTile.setState(Orientation.REGULAR, Rotation.REGULAR)

  def getOppositeDirection(self, direction):
    if direction == Edge.UPPER:
      return Edge.LOWER
    elif direction == Edge.LOWER:
      return Edge.UPPER
    elif direction == Edge.LEFT:
      return Edge.RIGHT
    else:
      return Edge.LEFT

  def moveAllTheWay(self, direction):
    visitedTiles = []
    moveSuccess = True
    while moveSuccess:
      visitedTiles.append(OrientedTile(self.currentTile))
      moveSuccess = self.tryMove(direction)
    return visitedTiles

  def tryMove(self, direction):
    if not self.currentTile.hasState():
      raise NotImplementedError()
    moveEdge = self.currentTile.getEdge(direction)
    complimentaryEdgeDirection = self.getOppositeDirection(direction)
    edgeFound = False
    if DEBUG:
      print(f"Looking for next tile in direction {direction} for tile {self.currentTile.title}")
      print(f"Current tile state is: orientation={self.currentTile.orientation}, rotation={self.currentTile.rotation}")
    for tile in tiles:
      # don't match the same tile again
      if self.currentTile.title == tile.title:
        continue
      # if tile already has a state we know which edge to look at
      if tile.hasState():
        compareEdge = tile.getEdge(complimentaryEdgeDirection)
        if compareEdge == moveEdge:
          edgeFound = True
          if DEBUG:
            print(f"Found matching edge on tile {tile.title} with state orientation={tile.orientation},rotation={tile.rotation}")
            print(f"Matching edge is {moveEdge}")
          self.currentTile = tile

      # we don't have a state for this tile yet, look at all possible combinations and update state if match is found
      else:
        for orientation in all_orientations:
          for rotation in all_rotations:
            currentEdge = contentManipulator.getTransformedEdge(tile.contents, complimentaryEdgeDirection, orientation, rotation)
            if currentEdge == moveEdge:
              edgeFound = True
              tile.setState(orientation, rotation)
              self.currentTile = tile
              break
          if edgeFound:
            break
        if edgeFound:
          break
    if DEBUG:
      if not edgeFound:
        print(f"Unable to move into direction {direction}")
    return edgeFound

  def setCheckPoint(self):
    self.checkpoint = self.currentTile

  def resetToCheckPoint(self):
    self.currentTile = self.checkpoint

  def uncoverMap(self):
    orientedTileMap = []

    # start by moving all the way up
    self.moveAllTheWay(Edge.UPPER)
    # next move all the way left to find top left corner
    self.moveAllTheWay(Edge.LEFT)

    # now we proceed line by line, we set a checkpoint, move all the way to the right, then reset to left edge, move down and repeat
    moveDownSuccess = True
    while moveDownSuccess:
      self.setCheckPoint()
      visitedTiles = self.moveAllTheWay(Edge.RIGHT)
      orientedTileMap.append(visitedTiles)
      self.resetToCheckPoint()
      moveDownSuccess = self.tryMove(Edge.LOWER)
    
    return orientedTileMap

class MapBuilder():
  def __init__(self, orientedTileMap):
    self.orientedTileMap = orientedTileMap

  def printTileGrid(self):
    for line in self.orientedTileMap:
      for tile in line:
        print(f"{tile.title} ", end="")
      print("")

  def buildMap(self):
    map = []
    for tileRow in self.orientedTileMap:
      i = 0
      while i < len(tileRow[0].contents):
        mapRow = ""
        for tile in tileRow:
          mapRow += tile.contents[i]
        map.append(mapRow)
        i += 1
    return map

  def printLines(self, lines):
    for line in lines:
      print(line)

class MonsterFinder:
  def __init__(self, map):
    self.map = map
    self.validMonsterMarkers = ['#', 'O']

  def findMonsters(self):
    for orientation in all_orientations:
      for rotation in all_rotations:
        print(f"check for monsters with configuration: orientation={orientation},rotation={rotation}")
        current_monster_template = contentManipulator.transformContentForOrientation(monster_template, orientation, rotation)
        self.markMonstersWithTemplate(current_monster_template)
  
  def markMonstersWithTemplate(self, monster):
    monsterWidth = len(monster[0])
    monsterHeight = len(monster)
    leftMostCheckIndex = 0
    rightMostCheckIndex = len(map)-monsterWidth-1
    topMostCheckIndex = 0
    bottomMostCheckIndex = len(map)-monsterHeight-1

    x = leftMostCheckIndex
    while x <= rightMostCheckIndex:
      y = topMostCheckIndex
      while y <= bottomMostCheckIndex:
        foundMonster = self.checkMonsterAtCoordinate(x, y, monster)
        if foundMonster:
          self.markMonsterAtCoordinate(x, y, monster)
        y += 1
      x += 1
  
  def checkMonsterAtCoordinate(self, x, y, monster):
    monsterWidth = len(monster[0])
    monsterHeight = len(monster)
    x_i = 0
    while x_i < monsterWidth:
      y_i = 0
      while y_i < monsterHeight:
        monsterContent = monster[y_i][x_i]
        # x=92,x_i=0,y=14,y_i=3
        # print(f"x={x},x_i={x_i},y={y},y_i={y_i}")
        mapContent = self.map[y+y_i][x+x_i]
        if monsterContent == "#" and not mapContent in self.validMonsterMarkers:
          return False
        y_i += 1
      x_i += 1
    return True

  def markMonsterAtCoordinate(self, x, y, monster):
    monsterWidth = len(monster[0])
    monsterHeight = len(monster)
    x_i = 0
    while x_i < monsterWidth:
      y_i = 0
      while y_i < monsterHeight:
        monsterContent = monster[y_i][x_i]
        mapContent = self.map[y+y_i][x+x_i]
        if monsterContent == "#":
          self.map[y+y_i] = self.map[y+y_i][:x+x_i] + "O" + self.map[y+y_i][x+x_i+1:]
        y_i += 1
      x_i += 1
    return True


f = open("input.txt", "r")
line = f.readline()
tiles = []
while line:
  tileLines = []
  while line.strip() != "":
    tileLines.append(line.strip())
    line = f.readline()
  tiles.append(Tile(tileLines))
  line = f.readline()

# tile explorer is the entity that is uncovering all tiles and setting the tile orientations
# tile navigator is the entity traversing the map of tiles once all orientations are set
print("uncovering map with TileExplorer")
tileExplorer = TileExplorer(tiles)
orientedTileMap = tileExplorer.uncoverMap()
print("finished uncovering map with TileExplorer")

mapBuilder = MapBuilder(orientedTileMap)
mapBuilder.printTileGrid()

map = mapBuilder.buildMap()
print("")
mapBuilder.printLines(map)

monsterFinder = MonsterFinder(map)
monsterFinder.findMonsters()

markedMap = monsterFinder.map
print("")
print("marked map:")
print("")
mapBuilder.printLines(markedMap)

allCharacters = ""
for line in markedMap:
  allCharacters += line

harshness = len(allCharacters.replace(".","").replace("O",""))
print(f"harshness: {harshness}")