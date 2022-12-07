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

class Tile:
  def __init__(self, textualRepresentation):
    self.textualRepresentation = textualRepresentation
    self.initialize()
    self.orientation = Orientation.UNKNOWN
    self.rotation = Rotation.UNKNOWN

  def initialize(self):
    text = self.textualRepresentation.copy()

    # get tile title
    titleLine = text.pop(0)
    self.title = int(titleLine.split("Tile ")[1].split(":")[0])

    # get tile upper edge in binary representation - left to right
    upperEdge = text[0]
    self.upperEdge = upperEdge.replace(".", "0").replace("#", "1")

    # get tile lower edge in binary representation - left to right
    lowerEdge = text[len(text)-1]
    self.lowerEdge = lowerEdge.replace(".", "0").replace("#", "1")

    # get tile left edge in binary representation - top to bottom
    leftEdge = ""
    for line in text:
      leftEdge+=line[0]
    self.leftEdge = leftEdge.replace(".", "0").replace("#", "1")

    # get tile right edge in binary representation - top to bottom
    rightEdge = ""
    for line in text:
      rightEdge+=line[len(line)-1]
    self.rightEdge = rightEdge.replace(".", "0").replace("#", "1")

    self.edgeRotationMatrix = {
      Rotation.REGULAR: [self.upperEdge, self.rightEdge, self.lowerEdge, self.leftEdge],
      Rotation.DEG90: [self.rightEdge, self.flipEdge(self.lowerEdge), self.leftEdge, self.flipEdge(self.upperEdge)],
      Rotation.DEG180: [self.flipEdge(self.lowerEdge), self.flipEdge(self.leftEdge), self.flipEdge(self.upperEdge), self.flipEdge(self.rightEdge)],
      Rotation.DEG270: [self.flipEdge(self.leftEdge), self.upperEdge, self.flipEdge(self.rightEdge), self.lowerEdge]
    }

  def getEdgeSelectionIndex(self, direction):
    if direction == Edge.UPPER:
      return 0
    elif direction == Edge.LOWER:
      return 2
    elif direction == Edge.LEFT:
      return 3
    else:
      return 1

  def flipEdge(self, edge):
    flippedEdge = ""
    index = len(edge)-1
    while index >= 0:
      flippedEdge += edge[index]
      index -= 1
    return flippedEdge

  def transformEdgeForOrientation(self, orientation, edgeList):
    if orientation == Orientation.FLIPPED_HORIZONTALLY or orientation == Orientation.FLIPPED_ALL:
      temp = edgeList[0]
      edgeList[0] = edgeList[2]
      edgeList[2] = temp
      edgeList[1] = self.flipEdge(edgeList[1])
      edgeList[3] = self.flipEdge(edgeList[3])

    if orientation == Orientation.FLIPPED_VERTICALLY or orientation == Orientation.FLIPPED_ALL:
      temp = edgeList[1]
      edgeList[1] = edgeList[3]
      edgeList[3] = temp
      edgeList[0] = self.flipEdge(edgeList[0])
      edgeList[2] = self.flipEdge(edgeList[2])

    return edgeList

  def rotateContent90Degrees(self, content):
    rotatedContent = []
    contentLength = len(content)
    i = 0
    while i < contentLength:
      rotatedContent.append([])
      i += 1

    i = 0
    while i < contentLength:
      j = 1
      while j <= contentLength:
        itemToAppend = content[i][contentLength-j]
        rotatedContent[contentLength-j].append(itemToAppend)
        j += 1
      i += 1

    return rotatedContent

  def transformContentForOrientation(self, orientation, rotation):
    newContent = self.textualRepresentation.copy()
    del newContent[0]

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
      for i in 1..len(newContent):
        line = newContent[i-1]
        newLine = []
        for item in line:
          newLine.insert(0, item)
        newContent[i-1] = newLine

    return newContent
    

  def getTransformedEdge(self, direction, orientation, rotation):
    rotationAccountedEdges = self.edgeRotationMatrix[rotation]
    rotationAndOrientationAccountedEdges = self.transformEdgeForOrientation(orientation, rotationAccountedEdges.copy())
    return rotationAndOrientationAccountedEdges[self.getEdgeSelectionIndex(direction)]

  def setState(self, orientation, rotation):
    self.orientation = orientation
    self.rotation = rotation

  def hasState(self):
    return self.orientation != Orientation.UNKNOWN and self.rotation != Rotation.UNKNOWN

  def getEdge(self, direction):
    if self.orientation == Orientation.UNKNOWN or self.rotation == Rotation.UNKNOWN:
      raise NotImplementedError()
    return self.getTransformedEdge(direction, self.orientation, self.rotation)

class OrientedTile:
  def __init__(self, tile):
    if not tile.hasState():
      raise NotImplementedError()
    self.contents = tile.transformContentForOrientation(tile.orientation, tile.rotation)
    self.title = tile.title

class TileExplorer:
  def __init__(self, tiles):
    self.startTile = tiles[0]
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
            currentEdge = tile.getTransformedEdge(complimentaryEdgeDirection, orientation, rotation)
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

class MapPlotter():
  def __init__(self, orientedTileMap):
    self.orientedTileMap = orientedTileMap

  def printTileGrid(self):
    for line in self.orientedTileMap:
      for tile in line:
        print(f"{tile.title} ", end="")
      print("")

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

mapPlotter = MapPlotter(orientedTileMap)

gridSize = len(orientedTileMap)
# find top left corner
topLeftId = orientedTileMap[0][0].title
# find top right corner
topRightId = orientedTileMap[0][gridSize-1].title
# find bottom left corner
bottomLeftId = orientedTileMap[gridSize-1][0].title
# find bottom right corner
bottomRightId = orientedTileMap[gridSize-1][gridSize-1].title

print(topLeftId * topRightId * bottomLeftId * bottomRightId)

mapPlotter.printTileGrid()
