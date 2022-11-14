import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.animation import PillowWriter
import numpy as np
import os

history = True

def plot():
    dir_name = os.getcwd() + '/'
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
points[0] = points[0][10 - 1::10]
row, col = points[0].shape
minX = min(points[0], key=lambda x: x[0])[0] - 0.1
minY = min(points[0], key=lambda x: x[1])[1] - 0.1
maxX = max(points[0], key=lambda x: x[0])[0] + 0.1
maxY = max(points[0], key=lambda x: x[1])[1] + 0.1
#print(minX, minY, maxX, maxY)

fig, ax = plt.subplots(1, 1)
ax.set_xlim(minX, maxX)
ax.set_ylim(minY, maxY)

l = []

def animate(i):
    if not history: ax.clear()
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
                label='original', marker='o', color='b')
        # Set the x and y axis to display a fixed range
    ax.set_xlim(minX, maxX)
    ax.set_ylim(minY, maxY)


ani = FuncAnimation(fig, animate, frames=row,
                    interval=10, repeat=True, repeat_delay=5000)
plt.show()

# Save the animation as an animated GIF
#ani.save("animator/simulation.gif", dpi=300,writer=PillowWriter(fps=10))