import sys
import Controllers as Controllers
import Controllers.Robots as Robots
from Evolution import build_table_random, import_gen_group, export_run


Qtables = []
if "--import-generation" in sys.argv:
    gen_number = sys.argv[sys.argv.index("--import-generation")+1]
    group_number = sys.argv[sys.argv.index("--import-generation")+2]
    group = import_gen_group(gen_number, group_number)
    Qtables = [
        group[0],
        *group[1]
    ]
else:
    Qtables = [
        build_table_random(is_seeker=True),
        build_table_random(is_seeker=False),
        build_table_random(is_seeker=False),
        build_table_random(is_seeker=False),
        build_table_random(is_seeker=False)
    ]

controllers = []
if "--simulated" in sys.argv:
    controllers = [
        Controllers.AvoiderController(Robots.Simio(), Qtables[1]),
        Controllers.AvoiderController(Robots.Simio(), Qtables[2]),
        Controllers.AvoiderController(Robots.Simio(), Qtables[3]),
        Controllers.AvoiderController(Robots.Simio(), Qtables[4]),
        Controllers.SeekerController(Robots.Simio(), Qtables[0]) # seeker is always last
    ]
else:
    if sys.argv[1] == "avoider":
        controllers = [Controllers.AvoiderController(Robots.Thymio(), Qtables[1])]
    elif sys.argv[1] == "seeker":
        controllers = [Controllers.SeekerController(Robots.Thymio(), Qtables[0])]
    else:
        raise Exception(f"Illegal robot type: {sys.argv[1]}")


count = 10000
for i in range(count):
    for c in controllers:
        c.step(i)


if "--import-generation" in sys.argv:
        gen_number = int(sys.argv[sys.argv.index("--import-generation")+1])
        group_number = sys.argv[sys.argv.index("--import-generation")+2]
        arrs, fitness = zip(*[(c.Q, c.total_reward()) for c in reversed(controllers)])
        export_run(arrs, fitness, gen_number, group_number)
else:
    for c in controllers:
        if type(c) == Controllers.AvoiderController:
            print(c.robot.name, c.Q)
        print(c.total_reward())
        arrs, fitness = zip(*[(c.Q, c.total_reward()) for c in reversed(controllers)])
        print(fitness)
