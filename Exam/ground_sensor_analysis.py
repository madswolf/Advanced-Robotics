import sys
import statistics

lines = [x.split(",") for x in sys.stdin]
sens_l = [int(x[0]) for x in lines]
sens_r = [int(x[1]) for x in lines]

mean_l = statistics.mean(sens_l)
mean_r = statistics.mean(sens_r)

stdev_l = statistics.stdev(sens_l)
stdev_r = statistics.stdev(sens_r)

print(f"left mean:                {mean_l}")
print(f"right mean:               {mean_r}")
print(f"left standard deviation:  {stdev_l}")
print(f"right standard deviation: {stdev_r}")
