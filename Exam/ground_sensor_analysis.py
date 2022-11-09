import sys
import statistics

reflected, ambient = list(zip(*[x.split() for x in sys.stdin]))
ref_l, ref_r = list(zip(*[map(int, x.split(",")) for x in reflected]))
amb_l, amb_r = list(zip(*[map(int, x.split(",")) for x in ambient]))

mean_ref_l = statistics.mean(ref_l)
mean_ref_r = statistics.mean(ref_r)
mean_amb_l = statistics.mean(amb_l)
mean_amb_r = statistics.mean(amb_r)

stdev_ref_l = statistics.stdev(ref_l)
stdev_ref_r = statistics.stdev(ref_r)
stdev_amb_l = statistics.stdev(amb_l)
stdev_amb_r = statistics.stdev(amb_r)

print(f"reflected mean:                ({mean_ref_l}, {mean_ref_r})")
print(f"reflected standard deviation:  ({stdev_ref_l}, {stdev_ref_r})")
print(f"ambient mean:                  ({mean_amb_l}, {mean_amb_r})")
print(f"ambient standard deviation:    ({stdev_amb_l}, {stdev_amb_r})")
