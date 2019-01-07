import pulp
import random

import rota

num_weeks = 6

max_inhours_shifts_per_person = 2
max_oncall_shifts_per_person = 3

def random_person():
    teams = ['A', 'B', 'C', 'D', 'E', 'F']
    is_shadow = random.choice([True, False, False, False])
    return rota.Person(
        team = random.choice(teams),
        can_do_inhours = random.choice([True, True, True, True, False]),
        num_times_inhours = 0 if is_shadow else random.randint(0, 10),
        num_times_shadow = random.randint(0, 1) if is_shadow else 2,
        can_do_oncall = random.choice([True, True, True, True, False]),
        num_times_oncall = random.randint(0, 10),
        forbidden_weeks = random.sample(range(0, num_weeks), random.randint(0, 2))
    )

# http://listofrandomnames.com/
people = {
    'Arlette Mckeighan': random_person(),
    'Brant Paskett': random_person(),
    'Buffy Nowacki': random_person(),
    'Camille Whitmarsh': random_person(),
    'Danielle Bence': random_person(),
    'Don Mong': random_person(),
    'Eleni Brandy': random_person(),
    'Elvira Stefani': random_person(),
    'Eura Joseph': random_person(),
    'Gussie Fridley': random_person(),
    'Helen Jarrard': random_person(),
    'Jessie Ahlquist': random_person(),
    'Katerine Greenwood': random_person(),
    'Leticia Grable': random_person(),
    'Lucile Spanbauer': random_person(),
    'Nathanael Mejia': random_person(),
    'Randell Gingras': random_person(),
    'Santiago Mizer': random_person(),
    'Theodore Hagberg': random_person(),
    'Verda Streit': random_person()
}

var = rota.generate_model(num_weeks, max_inhours_shifts_per_person, max_oncall_shifts_per_person, people)

for week in range(num_weeks):
    print(f"\n== Week {week+1}:")
    for role in rota.Role:
        for person in people.keys():
            if pulp.value(var[week, person, role.name]) == 1:
                print(f"{role.name}: {person}")
