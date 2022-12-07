import os, sys
from Evolution import build_table_random, export_gen_groups, next_generation

evolution_data_folder = "Exam/EvolutionData"
groups_per_run = 8

def generate_gen1_input():
    participants = []
    for _ in range(1,1+groups_per_run):
        participants.append((
            build_table_random(),
            [build_table_random() for _ in range(4)]
        ))
    export_gen_groups(participants, 1)



def generate_input_for_next_gen(current_gen):
    new_seekers, new_avoiders = next_generation(current_gen)
    export_gen_groups((new_seekers, new_avoiders), current_gen+1)
    
        
def check_generation_finished(gen, groups):
    finished_groups = [line for line in open(f"{evolution_data_folder}/{gen}_finished.txt", "r")]
    return sorted(finished_groups) == sorted(groups)
    

if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise Exception("Missing arguments 'current_gen' or 'num_gens'")
        
    current_gen = int(sys.argv[1])
    num_gens = int(sys.argv[2])
    if current_gen == "0":
        generate_gen1_input()
    
    for current_gen in range(int(num_gens)):
        groups = range(1, 1+groups_per_run)
        for i in groups:
            os.subprocess(f"python Main.py --simulated --import-generation {current_gen} {i}")
        while(check_generation_finished(current_gen, groups)):
            os.sleep(0.1)
            