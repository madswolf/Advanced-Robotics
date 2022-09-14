import sys
from collections import deque
lines = sys.stdin.readlines()

diamond = '$'
goal = '.'
diamondOnGoal = '*'
robot = '@'
wall = '#'

width = len(lines[0].strip())
height = len(lines)

board = [[0 for _ in range(width)] for _ in range(height)]
# 0 = air
# 1 = wall
# 2 = goal

robotPos = (0,0)
robotDirection = 0
north = 0
south = 1
east = 2
west = 3
# 0 = north
# 1 = south
# 2 = east 
# 3 = west 

goalPosisitions = []
diamondPositions = []
for i in range(len(lines)):
    line = lines[i].strip()
    print("line equals", line)
    for j in range(len(line)):
        position = (i,j)
        symbol = line[j]
        print("symbol equals", symbol)
        if symbol is robot:
            print(1)
            robotPos = position
            board[i][j] = 0
        elif symbol is goal:
            print(2)
            goalPosisitions.append(position)
            board[i][j] = 2
        elif symbol is diamond:
            print(3)
            diamondPositions.append(position)
            board[i][j] = 0
        elif symbol is diamondOnGoal:
            print(4)
            board[i][j] = 2
            diamondPositions.append(position)
        elif symbol is wall:
            print(5)
            board[i][j] = 1
        else:
            print(6)
            board[i][j] = 0

for line in board:
    print(line)

air = 0
wall = 1
goal = 2

def goInDirection(pos, direction):
    if(direction == north):
        return (pos[0] - 1, pos[1])
    elif(direction == south):
        return (pos[0] + 1, pos[1])
    elif(direction == east):
        return (pos[0], pos[1] + 1)
    elif(direction == west):
        return (pos[0], pos[1] - 1)

def posToBoardState(pos):
    return board[pos[0]][pos[1]]

def isCorner(pos):
    up = posToBoardState(goInDirection(pos,north))
    down = posToBoardState(goInDirection(pos,south))
    left = posToBoardState(goInDirection(pos,east))
    right = posToBoardState(goInDirection(pos,west))

    if(
        up == wall and left == wall
        or up == wall and right == wall
        or down == wall and left == wall
        or down == wall and right == wall
        ):
        return True
    else:
        return False

def canGoInDirection(robotPos, diamonds, direction):
    newPos = goInDirection(robotPos, direction)
    print(newPos)
    if(posToBoardState(newPos) == wall): #moves into wall
        print("moved into wall")
        return False
    
    for diamondPos in diamonds:
        if(newPos == diamondPos):
            newDiamondPos = goInDirection(diamondPos, direction)
            for diamondPos2 in diamonds:
                if(newDiamondPos == diamondPos2):  #moves two diamonds
                    print("moves two diamonds")
                    return False 
            
            if (posToBoardState(newDiamondPos) == wall): #diamond moves into wall
                print("moved diamond into wall")
                return False
            if(isCorner(newDiamondPos) and posToBoardState(newDiamondPos) != goal): #moves into corner
                print("moved into corner")
                return False
            
    return True

def hasWon(state):
    currDiamondPos = state[1]
    print(goalPosisitions, currDiamondPos)
    return sorted(goalPosisitions) == sorted(currDiamondPos)

def updateDiamondPos(robotPos, currDiamondPos, direction):
    newDiamondPos = []
    for diamondPos in currDiamondPos:
        if diamondPos == goInDirection(robotPos, direction):
            diamondPos = goInDirection(diamondPos, direction)
        newDiamondPos.append(diamondPos)
    return newDiamondPos

states = deque([[robotPos, diamondPositions, []]])

def expandState(state):
    currRobotPos = state[0]
    currDiamondPos = state[1]
    moves = state[2]

    if(canGoInDirection(currRobotPos, currDiamondPos, north)):
        newDiamondPos = updateDiamondPos(currRobotPos, currDiamondPos, north)
        newMoves = moves.copy()
        newMoves.append(north)
        states.append([goInDirection(currRobotPos, north), newDiamondPos, newMoves])

    if(canGoInDirection(currRobotPos, currDiamondPos, south)):
        newDiamondPos = updateDiamondPos(currRobotPos, currDiamondPos, south)
        newMoves = moves.copy()
        newMoves.append(south)
        states.append([goInDirection(currRobotPos, south),newDiamondPos, newMoves])

    if(canGoInDirection(currRobotPos, currDiamondPos, east)):
        newDiamondPos = updateDiamondPos(currRobotPos, currDiamondPos, east)
        newMoves = moves.copy()
        newMoves.append(east)
        states.append([goInDirection(currRobotPos, east),newDiamondPos, newMoves])
    
    if(canGoInDirection(currRobotPos, currDiamondPos, west)):
        newDiamondPos = updateDiamondPos(currRobotPos, currDiamondPos, west)
        newMoves = moves.copy()
        newMoves.append(west)
        states.append([goInDirection(currRobotPos, west),newDiamondPos, newMoves])

print(diamondPositions, robotPos, goalPosisitions)

while len(states) != 0:
    state = states.popleft()
    if(hasWon(state)):
        print("has won")
        print(state[2]) 
        break
    expandState(state)