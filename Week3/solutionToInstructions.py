robot_direction = 0 # 0=up, 1=right, 2=down, 3=left
instruction_output = []

def parse_moved_box(moves):
    output = []
    i = 0
    while i < len(moves):
        if moves[i] == "moved_box":
            if moves[i-1] != moves[i+1] and moves[i+1] != "stop":
                output.append("backwards")
        else:
            output.append(moves[i])
        i += 1
    return output

def rotate_move(move): # returns instruction according to current robot orientation, and sets new orientation
    global robot_direction
    move_order = ["up", "right", "down", "left"]
    cur_idx = move_order.index(move)
    new_move = move_order[(cur_idx - robot_direction) % len(move_order)]
    robot_direction = cur_idx
    return new_move

def step_move(move):
    global robot_direction
    if move == "backwards":
        instruction_output.append(instruction_output[-1]) # append extra instruction for pushing into the right square
        instruction_output.append("backwards")
        robot_direction = (robot_direction + 2) % 4
    elif move == "stop": instruction_output.append("stop")
    else:
        instruction_output.append(rotate_move(move))
        
def direction_to_index(direction):
    move_order = ["up", "right", "down", "left"]
    return move_order.index(direction)
        
moves = input().split()
moves.append("stop")
moves = parse_moved_box(moves)

human_instruction = moves[0]
robot_direction = int(direction_to_index(moves.pop(0)))
for m in moves:
    step_move(m)

instruction_output = instruction_output[:-1] + ["up", "stop"] # push one further at the end
print("Human! Face me " + human_instruction)
print(" ".join(instruction_output))
