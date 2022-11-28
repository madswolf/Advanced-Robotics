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
ref_r_reduced = reduce_list_to_occurrences(ref_r)
amb_l_reduced = reduce_list_to_occurrences(amb_l)
amb_r_reduced = reduce_list_to_occurrences(amb_r)


fig, axs = plt.subplots(2,2)
axs[0,0].bar(ref_l_reduced[0], ref_l_reduced[1], label="reflected left")
axs[0,1].bar(ref_r_reduced[0], ref_r_reduced[1], label="reflected right", color="tab:orange")
axs[1,0].bar(amb_l_reduced[0], amb_l_reduced[1], label="ambient left", color="tab:green")
axs[1,1].bar(amb_r_reduced[0], amb_r_reduced[1], label="ambient right", color="tab:red")
axs[1,0].set_xticks([0,1,2,3,4])
axs[1,1].set_xticks([0,1,2,3,4])
axs[0,0].axvline(x=mean_ref_l, color="r", linestyle="--")
axs[0,1].axvline(x=mean_ref_r, color="r", linestyle="--")
axs[1,0].axvline(x=mean_amb_l, color="r", linestyle="--")
axs[1,1].axvline(x=mean_amb_r, color="r", linestyle="--")
axs[0,0].set(xlabel="values", ylabel="occurrences", title=f"Reflected left, mean: {mean_ref_l:0.2f}")
axs[0,1].set(xlabel="values", ylabel="occurrences", title=f"Reflected right, mean: {mean_ref_r:0.2f}")
axs[1,0].set(xlabel="values", ylabel="occurrences", title=f"Ambient left, mean: {mean_amb_l:0.2f}")
axs[1,1].set(xlabel="values", ylabel="occurrences", title=f"Ambient right, mean: {mean_amb_r:0.2f}")

plt.show()

print(f"reflected mean:                ({mean_ref_l}, {mean_ref_r})")
print(f"reflected standard deviation:  ({stdev_ref_l}, {stdev_ref_r})")
print(f"ambient mean:                  ({mean_amb_l}, {mean_amb_r})")
print(f"ambient standard deviation:    ({stdev_amb_l}, {stdev_amb_r})")
