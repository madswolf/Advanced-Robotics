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

def export_run(arrs: list[np.ndarray], fitness: list[float], name: str):
    for (arr,rew) in zip(arrs, fitness):
        np.save(f"{evolution_data_folder}/{name}.npy", arr)
        np.save(f"{evolution_data_folder}/{name}.npy", np.asarray([rew]))


def import_run(name):
    with open(f"{evolution_data_folder}{name}.npy", "rb") as f:
        seeker = np.load(f)
        seeker_fitness = np.load(f)[0]
        avoiders = [(np.load(f), np.load(f)) for _ in range(8)]
        return ((seeker, seeker_fitness), avoiders)


def import_generation(number):
    files = os.listdir(evolution_data_folder)
    this_gen = [s for s in files if s.endswith(f"gen{number}.npy")]
    runs = [import_run(s) for s in this_gen]
    return [(x[0], *x[1]) for x in runs] # (seekers, avoiders)
    

def elitism(participants: list[tuple[np.ndarray, float]]):
    ranked = sorted(participants, key=lambda x: x[1])
    if len(ranked) % 2 != 0:
        raise "Generation has odd number of subjects. Cannot generate next generation"
    return ranked[len(ranked)/2:]


def pair_participants(participants: list[np.ndarray]):
    output = []
    for _ in range(4):
        pairing_sequence = shuffle(range(len(participants)))
        for i in range(len(pairing_sequence)):
            if(i % 2 == 1):
                pass
            output.append(
                participants[i],
                participants[i+1]
            )
    return output


def next_generation(number):
    cur_seekers, cur_avoiders = import_generation(number)
    surviving_seekers = elitism(cur_seekers)
    surviving_avoiders = elitism(cur_avoiders)
    seeker_pairs = pair_participants(surviving_seekers)
    avoider_pairs = pair_participants(surviving_avoiders)
    new_seekers = [breed(x[0], x[1], True) for x in seeker_pairs]
    new_avoiders = [breed(x[0], x[1], False) for x in avoider_pairs]

    return new_seekers, new_avoiders


def export_gen_groups(participants, number):
    if len(participants[0]) != len(participants[1]) * 4:
        raise "Incorrect seeker/avoider ratio"
    
    for i in range(len(participants[0])):
        np.save(f"{evolution_data_folder}/gen{number}_input_group{i}.npy", participants[0][i])
        np.save(f"{evolution_data_folder}/gen{number}_input_group{i}.npy", participants[1][i*4])
        np.save(f"{evolution_data_folder}/gen{number}_input_group{i}.npy", participants[1][i*4+1])
        np.save(f"{evolution_data_folder}/gen{number}_input_group{i}.npy", participants[1][i*4+2])
        np.save(f"{evolution_data_folder}/gen{number}_input_group{i}.npy", participants[1][i*4+3])


def import_gen_group(number, group):
    with open(f"{evolution_data_folder}/gen{number}_input_group{group}.npy", "rb") as f:
        seeker = np.load(f)
        avoiders = [np.load(f) for _ in range(4)]
        return seeker, avoiders