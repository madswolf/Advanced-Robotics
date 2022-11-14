import sys
import statistics
from matplotlib import pyplot as plt

def reduce_list_to_occurrences(lst):
    counts = {}
    for i in lst:
        if i in counts.keys():
            counts[i] = counts[i] + 1
        else:
            counts[i] = 1
    return list(zip(*sorted([(x, counts[x]) for x in counts])))

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

ref_l_reduced = reduce_list_to_occurrences(ref_l)
print(ref_l_reduced[0])
ref_r_reduced = reduce_list_to_occurrences(ref_r)

plt.plot(ref_l_reduced[0], ref_l_reduced[1], label="reflected left")
plt.plot(ref_r_reduced[0], ref_r_reduced[1], label="reflected right")
plt.legend()
plt.show()

print(f"reflected mean:                ({mean_ref_l}, {mean_ref_r})")
print(f"reflected standard deviation:  ({stdev_ref_l}, {stdev_ref_r})")
print(f"ambient mean:                  ({mean_amb_l}, {mean_amb_r})")
print(f"ambient standard deviation:    ({stdev_amb_l}, {stdev_amb_r})")
