#!/usr/bin/python3
import numpy as np
from random import random, shuffle
import os
from Models.IllegalActions import IllegalActions, IllegalStateActions, IllegalZoneActions 

from Controllers import RobotController, AvoiderController, SeekerController

evolution_data_folder = "Exam/EvolutionData"

def build_table_random(is_seeker):
    Q = np.random.random_sample((3, 10, 5))
    return disallow_illegal_actions(Q, is_seeker)

def crossover_tables(t1: np.ndarray, t2: np.ndarray):
    Q = t2.copy()
    for idx1, x in enumerate(t1):
        for idx2, y in enumerate(x):
            rand = round(random())
            for idx3, z in enumerate(y):
                if idx3 % 2 == rand:
                    Q[idx1][idx2][idx3] = z
    return Q

def mutate_table(t: np.ndarray, is_seeker:bool):
    Q = t.copy()
    for idx1, x in enumerate(t):
        for idx2, y in enumerate(x):
            for idx3, z in enumerate(y):
                if random() > 0.1:
                    Q[idx1][idx2][idx3] = random()
    return disallow_illegal_actions(Q, is_seeker)

def breed(t1: np.ndarray, t2: np.ndarray, is_seeker: bool):
    baby = crossover_tables(t1, t2)
    return mutate_table(baby, is_seeker)

def disallow_illegal_actions(t: np.ndarray, is_seeker: bool):
    illegalZoneActions = \
        IllegalZoneActions.Seeker if is_seeker \
        else IllegalZoneActions.Avoider 

    for act in illegalZoneActions:
        t[act[0], :, act[1]] = -10

    illegalStateActions = \
        IllegalStateActions.Seeker if is_seeker \
        else IllegalStateActions.Avoider 
        
    for act in illegalStateActions:
        t[act[0], act[1], :] = -10

    
    illegalStateActions = \
        IllegalActions.Seeker if is_seeker \
        else IllegalActions.Avoider 
        
    for act in illegalStateActions: #don't weight illegal actions positively
        t[act[0], act[1], act[2]] = -10

    return t

def export_run(arrs, fitness, gen_number, group_number):
    name = f"gen{str(gen_number)}_group{group_number}"
    file = open(f"{evolution_data_folder}/{gen_number}_finished.txt", "a")
    file.write(f"{group_number}\n")
    file.flush()
    file.close()

    npy_file = open(f"{evolution_data_folder}/{name}.npy", "wb")
    for (arr,rew) in zip(arrs, fitness):
        np.save(npy_file, arr)
        np.save(npy_file, np.asarray([rew]))
    
    npy_file.close()
        

def import_run(file_name):
    file = open(f"{evolution_data_folder}/{file_name}","rb")
    seeker = np.load(file)
    seeker_fitness = np.load(file)[0]
    avoiders = []
    for _ in range(4):
        avoider = np.load(file)
        avoider_fitness = np.load(file)
        avoiders.append((avoider, avoider_fitness))
    return ((seeker, seeker_fitness), avoiders)


def import_generation(number):
    files = os.listdir(evolution_data_folder)
    this_gen = [s for s in files if s.startswith(f"gen{number}_group")]
    runs = [import_run(s) for s in this_gen]
    seekers = []
    avoiders = []
    for run in runs:
        seekers.append(run[0])
        for avoider in run[1]:
            avoiders.append(avoider)
            
    return (seekers, avoiders) # (seekers, avoiders)
    

def elitism(participants):
    sorter = lambda x: x[1]
    ranked = sorted(participants, key=sorter)
    if len(ranked) % 2 != 0:
        raise "Generation has odd number of subjects. Cannot generate next generation"
    return ranked[int(len(ranked)/2):]


def pair_participants(participants):
    output = []
    for _ in range(4):
        pairing_sequence = list(range(len(participants)))
        shuffle(pairing_sequence)
        for i in range(0, len(pairing_sequence), 2):
            #if(i % 2 == 1):
            #    pass
            pair_a_index = pairing_sequence[i]
            pair_b_index = pairing_sequence[i+1]

            output.append((
                participants[pair_a_index],
                participants[pair_b_index]
            ))
    return output

def export_alpha_and_omega(seekers, avoiders, number):
    sorter = lambda x: x[1]
    best_seeker = sorted(seekers, key=sorter)[len(seekers)-1]
    best_avoider = sorted(avoiders, key=sorter)[len(avoiders)-1]
    file = open(f"{evolution_data_folder}/gen{number}_alpha_omega_sigma.npy", "wb")
    np.save(file,best_seeker[0])
    np.save(file,best_avoider[0])
    finished_file = open(f"{evolution_data_folder}/{number}_finished.txt", "a")
    finished_file.write("best seeker reward: " + str(best_seeker[1]) + "\n")
    finished_file.write("best avoider reward: " + str(best_avoider[1]) + "\n")
    finished_file.write("average seeker reward: " + str(sum(x[1] for x in seekers)/len(seekers)) + "\n")
    finished_file.write("average avoider reward: " + str((sum(x[1] for x in avoiders)/len(avoiders))) + "\n")
    file.flush()
    file.close()

def next_generation(number):
    cur_seekers, cur_avoiders = import_generation(number)
    export_alpha_and_omega(cur_seekers, cur_avoiders, number)
    surviving_seekers = elitism(cur_seekers)
    surviving_avoiders = elitism(cur_avoiders)
    seeker_pairs = pair_participants(surviving_seekers)
    avoider_pairs = pair_participants(surviving_avoiders)
    new_seekers = [breed(x[0][0], x[1][0], True) for x in seeker_pairs]
    new_avoiders = [breed(x[0][0], x[1][0], False) for x in avoider_pairs]

    return new_seekers, new_avoiders


def export_gen_groups(participants, number):
    if len(participants[0]) * 4 != len(participants[1]):
        raise Exception("Incorrect seeker/avoider ratio")
    
    for i in range(len(participants[0])):
        file = open(f"{evolution_data_folder}/gen{number}_input_group{i}.npy", "wb")
        np.save(file, participants[0][i])
        np.save(file, participants[1][i*4])
        np.save(file, participants[1][i*4+1])
        np.save(file, participants[1][i*4+2])
        np.save(file, participants[1][i*4+3])
        file.flush()
        file.close()


def import_gen_group(number, group):
    with open(f"{evolution_data_folder}/gen{number}_input_group{group}.npy", "rb") as f:
        seeker = np.load(f)
        avoiders = [np.load(f) for _ in range(4)]
        return seeker, avoiders

def import_gen_best(number):
    #gen0_alpha_omega_sigma.npy
    with open(f"{evolution_data_folder}/gen{number}_alpha_omega_sigma.npy", "rb") as f:
        seeker = np.load(f)
        avoider = np.load(f)
        return seeker, avoider


if __name__ == "__main__":
    print(next_generation(0))