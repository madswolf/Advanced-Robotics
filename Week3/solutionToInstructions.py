robot_direction = 0 # 0=up, 1=right, 2=down, 3=left
instruction_output = []

def rotate_move(move): # returns instruction according to current robot orientation, and sets new orientation
    move_order = ["up", "right", "down", "left"]
    cur_idx = move_order.index(move)
    new_move = move_order[(cur_idx - robot_direction) % len(move_order)]
    robot_direction = cur_idx
    return new_move

def step_move(move):
    if move == "backwards":
        instruction_output.append("backwards")
        robot_direction = (robot_direction + 2) % 4
        return
    else:
        instruction_output.append(rotate_move(move))
        
        
moves = input().split()

for m in moves:
    step_move(m)

print(instruction_output)
