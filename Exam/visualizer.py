import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np
import os
from math import atan, radians, cos, sin, pi

files = []

def color_from_file(file):
    if "Hamilton" in file:
        return 'lightblue'
    elif "Lando" in file:
        return 'orange'
    elif "Alonso" in file:
        return 'darkblue'
    elif "Stroll" in file:
        return 'green'
    elif "Verstappen" in file:
        return "red"


def plot():
    global files
    dir_name = os.getcwd() + '/Exam/trajectories/'
    files = os.listdir(dir_name)
    files.sort(reverse=True)
    files = files[:5]
    vectors = []
    for item in files:
        if item.endswith(".dat"):
            with open(dir_name+item, 'r') as f:
                lines = f.readlines()
                vector_list = [list(map(float, line.split(", "))) for line in lines]
                vectors_set = np.array(vector_list)
            
            vectors.append(vectors_set)
    return vectors

points = plot()
for i in range(len(points)):
    points[i] = points[i][50 - 1::50]

shortest_trajectory_index = min(range(len(points)), key=lambda i: len(points[i]))
row, col = points[shortest_trajectory_index].shape

minX = min(min([min(p[:, 0]) for p in points]) - 0.1, -1.2)
maxX = max(max([max(p[:, 0]) for p in points]) + 0.1, 1.2)
minY = min(min([min(p[:, 1]) for p in points]) - 0.1, -1.2)
maxY = max(max([max(p[:, 1]) for p in points]) + 0.1, 1.2)
print(minX, maxX, minY, maxY)

fig, ax = plt.subplots(1, 1)
ax.set_xlim(minX, maxX)
ax.set_ylim(minY, maxY)

def animate(i):
    global files
    ax.clear()
    ax.axvline(x=-1, color="r", linestyle="--")
    ax.axvline(x=1, color="r", linestyle="--")
    ax.axhline(y=1, color="r", linestyle="--")
    ax.axhline(y=-1, color="r", linestyle="--")
    
    # Get the point from the points list at index i
    # point = points[i]
    for idx, p in enumerate(points):
        xs = p[i, 0]
        ys = p[i, 1]
        x = [xs, p[i, 2] + xs]
        y = [ys, p[i, 3] + ys]
        
        if "Verstappen" in files[idx]:
            front_fov = radians(30)
            view_distance = 0.4
            a = (y[1]-y[0]) / (x[1]-x[0])
            angle = atan(a)
            if x[1] < x[0]: angle -= pi
            x1 = x[0] + cos(angle + front_fov) * view_distance
            x2 = x[0] + cos(angle - front_fov) * view_distance
            y1 = y[0] + sin(angle + front_fov) * view_distance
            y2 = y[0] + sin(angle - front_fov) * view_distance
            triangle = plt.Polygon([[x[0], y[0]], [x1, y1], [x2, y2]], color=color_from_file(files[idx]), alpha=0.5)
            ax.add_patch(triangle)

            angle2 = angle+radians(180)
            back_fov = radians(15)
            x1b = x[0] + cos(angle2 + back_fov) * view_distance
            x2b = x[0] + cos(angle2 - back_fov) * view_distance
            y1b = y[0] + sin(angle2 + back_fov) * view_distance
            y2b = y[0] + sin(angle2 - back_fov) * view_distance
            triangle2 = plt.Polygon([[x[0], y[0]], [x1b, y1b], [x2b, y2b]], color=color_from_file(files[idx]), alpha=0.5)
            ax.add_patch(triangle2)

            
        circle = plt.Circle((xs, ys), 0.095, color=color_from_file(files[idx]), alpha=0.2)
        ax.add_patch(circle)

        # Plot that point using the x and y coordinates
        
        ax.plot(x, y, "-", linewidth=2, color=color_from_file(files[idx]))
        
        ax.plot(xs, ys,
                label='original', marker='o', color=color_from_file(files[idx]))
        
        # Set the x and y axis to display a fixed range
    ax.set_xlim(minX, maxX)
    ax.set_ylim(minY, maxY)

print("plotting files: ", files)
ani = FuncAnimation(fig, animate, frames=row,
                    interval=10, repeat=True, repeat_delay=3000)
plt.show()

# Save the animation as an animated GIF
current_time = time.strftime("%m-%d--%H_%M")
#ani.save("trajectories/simulation_" + str(current_time) + ".gif", dpi=300,writer=PillowWriter(fps=10))