def to_map_coords(x,y):
    return (x/60, y/60)

def facing_target(current_coords, target_coords):
    distance = [target_coords[0] - current_coords[0], target_coords[1] - current_coords[0]]
    a = numpy.degrees(numpy.arctan(distance[1] / distance[0]))

    if(a - current_coords[2] < 0):
        return "left"
    else: 
        return "right"

    return "correct"



def turn_to_target(current_coords, target_coords):
    facing = facing_target(current_coords, target_coords)
    
    while(facing != "correct"):
        if (facing == "left"):
            robot.drive(-50,50)
        else: #right
            robot.drive(50,-50)
        facing = facing_target(current_coords, target_coords)
    
    robot.drive(0,0)