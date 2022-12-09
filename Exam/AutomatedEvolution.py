#!/usr/bin/python3
import os, sys, subprocess, time
from yaspin import yaspin
from Evolution import build_table_random, export_gen_groups, next_generation
import time

evolution_data_folder = "Exam/EvolutionData"
groups_per_run = 8

def generate_gen0_input():
    print("generating")
    seekers = []
    avoiders = []
    for _ in range(groups_per_run):
        seekers.append(build_table_random(True))
        for _ in range(4):
            avoiders.append(build_table_random(False))

    export_gen_groups([seekers, avoiders], 0)

def generate_input_for_next_gen(current_gen):
    new_seekers, new_avoiders = next_generation(current_gen)
    export_gen_groups((new_seekers, new_avoiders), current_gen+1)

        
def check_generation_finished(gen, groups):
    finished_groups = [int(groupname) for groupname in open(f"{evolution_data_folder}/{gen}_finished.txt", "r")]
    return sorted(finished_groups) == sorted(groups)

def write_elapsed(gen, elapsed):
    file = open(f"{evolution_data_folder}/{gen}_finished.txt", "a")
    file.write("elapsed time: {:.2f}s \n".format(elapsed))
    file.flush()
    file.close()

def simulate_gen(current_gen):
    print(f"gen{current_gen}")
    start = time.time()
    finished_file = open(f"{evolution_data_folder}/{current_gen}_finished.txt", "w")
    finished_file.close()
    groups = range(groups_per_run)
    for i in groups:
        log = open(f"{evolution_data_folder}/log_gen{current_gen}_group{i}.log","a")
        log.write("begin")
        log.flush()
        subprocess.Popen(f"python Exam/Main.py --simulated --no-visualization --import-generation {current_gen} {i}",stdout=log, shell=False)
    while not check_generation_finished(current_gen, groups):
        print("waiting")
        if time.time() - start > 60:
            simulate_gen(current_gen)
            return
        time.sleep(1)
    end = time.time()
    write_elapsed(current_gen, end-start)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise Exception("Missing arguments 'current_gen' or 'num_gens'")
        
    current_gen = int(sys.argv[1])
    num_gens = int(sys.argv[2])
    if current_gen == 0:
        generate_gen0_input()

    for current_gen in range(current_gen, current_gen + num_gens):
        simulate_gen(current_gen)
        generate_input_for_next_gen(current_gen)
            