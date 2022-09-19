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
north = 'u'
south = 'd'
east = 'r'
west = 'l'
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

class State:
    def __init__(self, robotPos, diamondPos):
        self.robotPos = robotPos
        self.diamondPos = diamondPos

class Node:
    def __init__(self, state:State, parentNode, moveDirection):
        self.state = state
        self.parentNode = parentNode
        self.moveDirection = moveDirection

# state is (robot pos, diamondPositions, parentStateIndex, moveDirection) 
nodes = deque()
goalPosisitions = goalPosisitions
startNode = Node(State(robotPos, diamondPositions), None, None)
nodes.append(startNode)
exploredStates = set()

def hasWon(node:Node):
    currDiamondPos = node.state.diamondPos
    #print(goalPosisitions, currDiamondPos)
    return sorted(goalPosisitions) == sorted(currDiamondPos)

def exPandDirectionIfPossible(state:State, parentNode:Node, direction):
    #print("start expansion")
    newPos = goInDirection(state.robotPos, direction)
    #print("oldpos ", state.robotPos, " -> new pos ", newPos)
    currDiamondPos = state.diamondPos
    if(posToBoardState(newPos) == wall): #moves into wall
        #print("moved into wall")
        return
    for i in range(len(currDiamondPos)):
        diamondPos = currDiamondPos[i]
        if(newPos == diamondPos):
            #print("moved diamond")
            newDiamondPos = goInDirection(diamondPos, direction)
            #print(newDiamondPos)
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
    #print("adding node:", newPos, currDiamondPos)
    nodes.append(Node(State(newPos, currDiamondPos), parentNode, direction))
    #print("end expansion")

def expandState(node:Node):
    global exploredStates
    #print(exploredStates)
    currDiamondPos = frozenset(node.state.diamondPos)
    testState  = (node.state.robotPos, currDiamondPos)
    #print(testState)
    if(testState not in exploredStates): 
        exploredStates.add((node.state.robotPos, currDiamondPos))

        exPandDirectionIfPossible(State(node.state.robotPos, node.state.diamondPos.copy()), node, north)
        exPandDirectionIfPossible(State(node.state.robotPos, node.state.diamondPos.copy()), node, south)
        exPandDirectionIfPossible(State(node.state.robotPos, node.state.diamondPos.copy()), node, east)
        exPandDirectionIfPossible(State(node.state.robotPos, node.state.diamondPos.copy()), node, west)
    #else:
    #    print(node, "was explored")

print(diamondPositions, robotPos, goalPosisitions)

currDepth = 0
print(nodes)
iterations = 0
finishnode = startNode
while len(nodes) != 0:
    iterations += 1
    node = nodes.popleft()
    #print(node, exploredStates)
    #print(state)
    #if(iterations % 1000 == 0):
    #    print(iterations)
    if(hasWon(node)):
        print("has won")
        finishnode = node
        print(iterations)
        break
    expandState(node)
print("finished")

currNode = finishnode
path = ""
while(currNode.parentNode != None):
    path += str(currNode.moveDirection)
    currNode = currNode.parentNode
print(path[::-1])
#for state in exploredStates:
#    print(state)