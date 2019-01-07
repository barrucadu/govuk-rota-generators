import pulp
import random

import rota

num_weeks = 12

max_inhours_shifts_per_person = 2
max_oncall_shifts_per_person = 3

def random_team():
    return random.choice(['A', 'B', 'C', 'D', 'E', 'F'])

def random_leave():
    return random.sample(range(0, num_weeks), random.randint(0, 0))

def random_shadow():
    return rota.Person(
        team = random_team(),
        can_do_inhours = True,
        num_times_inhours = 0,
        num_times_shadow = random.randint(0, 1),
        can_do_oncall = False,
        num_times_oncall = 0,
        forbidden_weeks = random_leave()
    )

def random_oncall():
    return rota.Person(
        team = random_team(),
        can_do_inhours = True,
        num_times_inhours = random.randint(0, 25),
        num_times_shadow = 2,
        can_do_oncall = True,
        num_times_oncall = random.randint(2,3),
        forbidden_weeks = random_leave()
    )

def random_inhours():
    return rota.Person(
        team = random_team(),
        can_do_inhours = True,
        num_times_inhours = random.randint(0, 25),
        num_times_shadow = 2,
        can_do_oncall = False,
        num_times_oncall = 0,
        forbidden_weeks = random_leave()
    )

# http://listofrandomnames.com/
# 6 shadows; 30 non-shadows, 11 of which are oncall
people = {
    'Allyson Mirando': random_shadow(),
    'Arlette Mckeighan': random_shadow(),
    'Brant Paskett': random_shadow(),
    'Breana Mar': random_shadow(),
    'Buffy Nowacki': random_shadow(),
    'Camille Whitmarsh': random_shadow(),
    'Danielle Bence': random_oncall(),
    'David Reifsteck': random_oncall(),
    'Delisa Polson': random_oncall(),
    'Don Mong': random_oncall(),
    'Eleni Brandy': random_oncall(),
    'Elvira Stefani': random_oncall(),
    'Eura Joseph': random_oncall(),
    'Galen Takemoto': random_oncall(),
    'Gussie Fridley': random_oncall(),
    'Hector Beckett': random_oncall(),
    'Helen Jarrard': random_oncall(),
    'Isaura Lafuente': random_inhours(),
    'Jessie Ahlquist': random_inhours(),
    'Katerine Greenwood': random_inhours(),
    'Kristen Youngren': random_inhours(),
    'Kristyn Wolverton': random_inhours(),
    'Leticia Grable': random_inhours(),
    'Lucile Spanbauer': random_inhours(),
    'Lynn Steinhauer': random_inhours(),
    'Mauro Au': random_inhours(),
    'Nathanael Mejia': random_inhours(),
    'Randell Gingras': random_inhours(),
    'Raye Slone': random_inhours(),
    'Reynalda Botelho': random_inhours(),
    'Santiago Mizer': random_inhours(),
    'Sergio Mcdevitt': random_inhours(),
    'Theodore Hagberg': random_inhours(),
    'Verda Streit': random_inhours(),
    'Werner Rosenblatt': random_inhours(),
    'Wilfredo Yoshida': random_inhours()
}

var = rota.generate_model(num_weeks, max_inhours_shifts_per_person, max_oncall_shifts_per_person, people)

for week in range(num_weeks):
    print(f"\n== Week {week+1}:")
    for role in rota.Role:
        for person, p in people.items():
            if pulp.value(var[week, person, role.name]) == 1:
                print(f"{role.name}: {person} {p}")
