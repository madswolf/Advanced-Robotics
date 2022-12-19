import os, sys, subprocess, time
import Controllers.Robots as Robots
import numpy as np
import sys
import Controllers as Controllers
from Evolution import build_table_random, import_gen_group, import_gen_best, export_run

before_chain="Before_safe_learn_gen410_alpha_omega_sigma"
after_chain="After_learn_continued_gen1685_alpha_omega_sigma"
evolution_data_folder = "Exam/evolution_chain_data"


def import_chain(name):
    with open(f"{evolution_data_folder}/{name}.npy", "rb") as f:
        seeker = np.load(f)
        avoider = np.load(f)
        return seeker, avoider
        
def run_chain(chain):
    group = import_chain(chain)
    Qtables = [
        group[0],
        group[1],
        group[1],
        group[1],
        group[1]
    ]

    data = []

    for i in range(50):
        simios = [
            Robots.Simio(),
            Robots.Simio(),
            Robots.Simio(),
            Robots.Simio(),
            Robots.Simio()
        ]
        seeker = Controllers.SeekerController(simios[4], Qtables[0])
        controllers = [
            Controllers.AvoiderController(simios[0], Qtables[1], seeker),
            Controllers.AvoiderController(simios[1], Qtables[2], seeker),
            Controllers.AvoiderController(simios[2], Qtables[3], seeker),
            Controllers.AvoiderController(simios[3], Qtables[4], seeker),
            seeker # seeker is always last
        ]
        count = 1000
        for j in range(count):
            for c in controllers:
                c.step(j)
        survived = 4 - controllers[4].tag_count
        untagged = filter(lambda x: not x.robot.tagged and not x.isSeeker, controllers)
        data.append((survived,[x.safe_steps for x in untagged]))

    return data

print(run_chain(before_chain))
print(run_chain(after_chain))
