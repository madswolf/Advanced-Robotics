import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np
import os

def plot():
    dir_name = os.getcwd() + '/trajectories/'
    test = os.listdir(dir_name)
    vectors = []
    for item in test:
        if item.endswith(".dat"):
            with open(dir_name+item, 'r') as f:
                lines = f.readlines()
                vector_list = [list(map(float, line.split(", "))) for line in lines]
                vectors_set = np.array(vector_list)
            
            vectors.append(vectors_set)
    return vectors

points = plot()
for i in range(len(points)):
    points[i] = points[i][10 - 1::10]

shortest_trajectory_index = min(range(len(points)), key=lambda i: len(points[i]))
row, col = points[shortest_trajectory_index].shape

minX = min([min(p[:, 0]) for p in points]) - 0.1
maxX = max([max(p[:, 0]) for p in points]) + 0.1
minY = min([min(p[:, 1]) for p in points]) - 0.1
maxY = max([max(p[:, 1]) for p in points]) + 0.1
print(minX, maxX, minY, maxY)

fig, ax = plt.subplots(1, 1)
ax.set_xlim(minX, maxX)
ax.set_ylim(minY, maxY)

def animate(i):
    ax.clear()
    # Get the point from the points list at index i
    # point = points[i]
    for p in points:
        xs = p[i, 0]
        ys = p[i, 1]
        x = [xs, p[i, 2] + xs]
        y = [ys, p[i, 3] + ys]
        # Plot that point using the x and y coordinates
        ax.plot(x, y, "-", linewidth=2, color='g')

        ax.plot(xs, ys,
                label='original', marker='o')
        # Set the x and y axis to display a fixed range
    ax.set_xlim(minX, maxX)
    ax.set_ylim(minY, maxY)


ani = FuncAnimation(fig, animate, frames=row,
                    interval=10, repeat=True, repeat_delay=3000)
plt.show()

# Save the animation as an animated GIF
current_time = time.strftime("%m-%d--%H_%M")
ani.save("trajectories/simulation_" + str(current_time) + ".gif", dpi=300,writer=PillowWriter(fps=10))