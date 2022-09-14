import sys
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
            robot = position
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

print(diamondPositions)        
print(goalPosisitions) 
print(robotPos)       

def goInDirection(pos, direction):
    if(direction == north):
        return (pos[0] - 1, pos[1])
    elif(direction == south):
        return (pos[0] + 1, pos[1])
    elif(direction == east):
        return (pos[0], pos[1] + 1)
    elif(direction == east):
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

def canGoInDirection(robotPos, direction, diamonds):
    newPos = goInDirection(robotPos, direction)
    
    if(posToBoardState(newPos) == wall):
        return False
    
    for diamondPos in diamonds:
        if(newPos == diamondPos):
            newDiamondPos = goInDirection(diamondPos, direction)
            for diamondPos2 in diamonds:
                if(newDiamondPos == diamondPos2 
                or posToBoardState(newDiamondPos) == wall
                ):
                    return False
