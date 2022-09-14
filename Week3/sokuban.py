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
            goalPosisitions.append(position)
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
    up = posToBoardState(goInDirection(pos, north))
    down = posToBoardState(goInDirection(pos, south))
    left = posToBoardState(goInDirection(pos, east))
    right = posToBoardState(goInDirection(pos, west))

    if(
        up != wall and down != wall
        or right != wall and left != wall
        ):
        return False
    else:
        return True

states = deque([[robotPos, diamondPositions, []]])

def hasWon(state):
    currDiamondPos = state[1]
    #print(goalPosisitions, currDiamondPos)
    return sorted(goalPosisitions) == sorted(currDiamondPos)

def exPandDirectionIfPossible(currRobotPos, currDiamondPos, moves, direction):
    newPos = goInDirection(currRobotPos, direction)
    #print(newPos)
    if(posToBoardState(newPos) == wall): #moves into wall
        #print("moved into wall")
        return
    
    for i in range(len(currDiamondPos)):
        diamondPos = currDiamondPos[i]
        if(newPos == diamondPos):
            newDiamondPos = goInDirection(diamondPos, direction)
            for diamondPos2 in currDiamondPos:
                if(newDiamondPos == diamondPos2):  #moves two diamonds
                    #print("moves two diamonds")
                    return
            currDiamondPos[i] = newDiamondPos
            
            newDiamondPosBoardState = posToBoardState(newDiamondPos) 

            if (newDiamondPosBoardState == wall): #diamond moves into wall
                #print("moved diamond into wall")
                return
            if(isCorner(newDiamondPos) and newDiamondPosBoardState != goal): #moves into corner
                #print("moved into corner")
                return
    newMoves = [*moves, direction]
    states.append([newPos, currDiamondPos, newMoves])

def expandState(state):
    currRobotPos = state[0]
    currDiamondPos = state[1]
    moves = state[2]

    exPandDirectionIfPossible(currRobotPos, currDiamondPos, moves, north)
    exPandDirectionIfPossible(currRobotPos, currDiamondPos, moves, south)
    exPandDirectionIfPossible(currRobotPos, currDiamondPos, moves, east)
    exPandDirectionIfPossible(currRobotPos, currDiamondPos, moves, west)

print(diamondPositions, robotPos, goalPosisitions)

currDepth = 0

while len(states) != 0:
    state = states.popleft()
    if(currDepth < len(state[2])):
        currDepth = len(state[2])
        print(currDepth)
    if(hasWon(state)):
        print("has won")
        print(state[2]) 
        break
    expandState(state)