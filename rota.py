import collections
import enum
import pulp
import random

# A person who can appear in the rota.  People have no names, as
# 'generate_model' is given a dict 'name -> person'.
Person = collections.namedtuple('Person', ['team', 'can_do_inhours', 'num_times_inhours', 'num_times_shadow', 'can_do_oncall', 'num_times_oncall', 'forbidden_weeks'])


class Role(enum.Enum):
    """All the different types of role.
    """

    PRIMARY          = enum.auto()
    SECONDARY        = enum.auto()
    SHADOW           = enum.auto()
    PRIMARY_ONCALL   = enum.auto()
    SECONDARY_ONCALL = enum.auto()


in_hours_roles = [Role.PRIMARY, Role.SECONDARY, Role.SHADOW]
on_call_roles  = [Role.PRIMARY_ONCALL, Role.SECONDARY_ONCALL]


def if_then(prob, var_a, k, var_b, var_d):
    """Translate 'if var_a > k then var_b >= 0 else var_b = 0' into ILP constraints.

    'var_d' must be a fresh decision variable.

    See http://www.yzuda.org/Useful_Links/optimization/if-then-else-02.html
    """

    # a number bigger than the number of times someone can actually be on shift
    m = 999999999

    prob += var_a - k + m * var_d >= 1
    prob += var_b + m * var_d >= 0
    prob += var_a - k <= 0 + m * (1 - var_d)
    prob += var_b <= m * (1 - var_d)


def generate_model(num_weeks, max_inhours_shifts_per_person, max_oncall_shifts_per_person, people):
    """Generate the mathematical model of the rota problem.
    """

    prob = pulp.LpProblem(name='2ndline rota', sense=pulp.LpMaximize)

    # Model the rota as a [num weeks x num people x num roles] matrix, where rota[week,person,role] == that person has that role for that week.
    rota = pulp.LpVariable.dicts('rota', ((week, person, role.name) for week in range(num_weeks) for person in people.keys() for role in Role), cat='Binary')

    # Auxilliary variable to track if someone is assigned
    assigned = pulp.LpVariable.dicts('assigned', people.keys(), cat='Binary')

    # Auxilliary variables to track the number of times someone has shadowed, been a non-shadow in-hours, or been on-call
    times_shadow  = pulp.LpVariable.dicts('times_shadow',  ((week, person) for week in range(num_weeks) for person in people.keys()), cat='Integer')
    times_inhours = pulp.LpVariable.dicts('times_inhours', ((week, person) for week in range(num_weeks) for person in people.keys()), cat='Integer')
    times_oncall  = pulp.LpVariable.dicts('times_oncall',  ((week, person) for week in range(num_weeks) for person in people.keys()), cat='Integer')

    # Auxilliary decision variable for if-then constructs
    # http://www.yzuda.org/Useful_Links/optimization/if-then-else-02.html
    d = pulp.LpVariable.dicts('d', ((week, person, role.name) for week in range(num_weeks) for person in people.keys() for role in Role), cat='Binary')

    ### Constraints

    # In every week:
    for week in range(num_weeks):
        # Constrain 'times_shadowed', 'times_inhoursed', and 'times_oncalled' auxilliary variables.
        for person, p in people.items():
            if week == 0:
                prob += times_shadow[week, person]  == p.num_times_shadow
                prob += times_inhours[week, person] == p.num_times_inhours
                prob += times_oncall[week, person]  == p.num_times_oncall
            else:
                prob += times_shadow[week, person]  == times_shadow[week - 1, person]  + rota[week - 1, person, Role.SHADOW.name]
                prob += times_inhours[week, person] == times_inhours[week - 1, person] + rota[week - 1, person, Role.PRIMARY.name]        + rota[week - 1, person, Role.SECONDARY.name]
                prob += times_oncall[week, person]  == times_oncall[week - 1, person]  + rota[week - 1, person, Role.PRIMARY_ONCALL.name] + rota[week - 1, person, Role.SECONDARY_ONCALL.name]

        # [1.1] Each role must be assigned to exactly one person, except shadow which may be unassigned.
        for role in Role:
            prob += pulp.lpSum(rota[week, person, Role.PRIMARY.name]          for person in people.keys()) == 1
            prob += pulp.lpSum(rota[week, person, Role.SECONDARY.name]        for person in people.keys()) == 1
            prob += pulp.lpSum(rota[week, person, Role.SHADOW.name]           for person in people.keys()) <= 1
            prob += pulp.lpSum(rota[week, person, Role.PRIMARY_ONCALL.name]   for person in people.keys()) == 1
            prob += pulp.lpSum(rota[week, person, Role.SECONDARY_ONCALL.name] for person in people.keys()) == 1

        # [1.2.1] Primary must: be able to do in-hours support
        # [1.3.1] Secondary must: be able to do in-hours support
        # [1.4.1] Shadow must: be able to do in-hours support
        # [1.5.1] Primary oncall must: be able to do out-of-hours support
        # [1.6.1] Secondary oncall must: be able to do out-of-hours support
        for person, p in people.items():
            prob += rota[week, person, Role.PRIMARY.name]          <= (1 if p.can_do_inhours else 0)
            prob += rota[week, person, Role.SECONDARY.name]        <= (1 if p.can_do_inhours else 0)
            prob += rota[week, person, Role.SHADOW.name]           <= (1 if p.can_do_inhours else 0)
            prob += rota[week, person, Role.PRIMARY_ONCALL.name]   <= (1 if p.can_do_oncall  else 0)
            prob += rota[week, person, Role.SECONDARY_ONCALL.name] <= (1 if p.can_do_oncall  else 0)

        # [1.2.2] Primary must: have been on in-hours support at least 3 times
        # [1.3.2] Secondary must: have shadowed at least twice
        # [1.6.2] Secondary oncall must: have done out-of-hours support at least 3 times
        for person in people.keys():
            if_then(prob, times_inhours[week, person], 2, rota[week, person, Role.PRIMARY.name],        d[week, person, Role.PRIMARY.name])
            if_then(prob, times_shadow[week, person],  1, rota[week, person, Role.SECONDARY.name],      d[week, person, Role.SECONDARY.name])
            if_then(prob, times_oncall[week, person],  2, rota[week, person, Role.PRIMARY_ONCALL.name], d[week, person, Role.PRIMARY_ONCALL.name])

    # A person must:
    for person, p in people.items():
        # Constrain 'assigned' auxilliary variable.
        for week in range(num_weeks):
            prob += assigned[person] >= pulp.lpSum(rota[week, person, role.name] for role in Role)

        # [1.4.2] Not shadow more than twice
        prob += times_shadow[num_weeks - 1, person] <= 2

        # [2.1] Not be assigned more than one role in the same week
        for week in range(num_weeks):
            prob += pulp.lpSum(rota[week, person, role.name] for role in Role) <= 1

        # [2.2] Not be assigned roles in two adjacent weeks
        for week in range(num_weeks):
            if week == num_weeks - 1:
                break
            prob += pulp.lpSum(rota[week, person, role.name] for role in Role) + pulp.lpSum(rota[week + 1, person, role.name] for role in Role) <= 1

        # [2.3] Not be assigned a role in a week they cannot do
        for forbidden_week in p.forbidden_weeks:
            prob += pulp.lpSum(rota[forbidden_week, person, role.name] for role in Role) == 0

        # [2.4] Not be assigned more than `max_inhours_shifts_per_person` in-hours roles in total
        prob += pulp.lpSum(rota[week, person, role.name] for week in range(num_weeks) for role in in_hours_roles) <= max_inhours_shifts_per_person

        # [2.5] Not be assigned more than `max_oncall_shifts_per_person` out-of-hours roles in total
        prob += pulp.lpSum(rota[week, person, role.name] for week in range(num_weeks) for role in on_call_roles) <= max_oncall_shifts_per_person

        # [2.6] Not be on in-hours support in the same week that someone else from their team is also on in-hours support
        for week in range(num_weeks):
            for person2, p2 in people.items():
                if person == person2:
                    continue
                if p.team != p2.team:
                    continue
                prob += pulp.lpSum(rota[week, person, role.name] for role in in_hours_roles) + pulp.lpSum(rota[week, person2, role.name] for role in in_hours_roles) <= 1

    ### Optimisations

    # [1] Minimise the maximum number of roles-assignments any one person has
    # or: Maximise the number of people with assignments
    # This is more important than the other optimisations (which are about reducing weeks which are bad in a fairly minor way) so give it a *1000 factor
    obj = pulp.lpSum(assigned[person] for person in people.keys()) * 1000

    # [2] Maximise the number of weeks where secondary has been on in-hours support fewer than 3 times
    obj += pulp.lpSum(rota[week, person, role.SECONDARY.name] for week in range(num_weeks) for person, p in people.items() if p.num_times_inhours < 3)

    # [3] Maximise the number of weeks where primary oncall has been on out-of-hours support fewer than 3 times
    obj += pulp.lpSum(rota[week, person, role.PRIMARY_ONCALL.name] for week in range(num_weeks) for person, p in people.items() if p.num_times_oncall < 3)

    # [4] Maximise the number of weeks with a shadow
    obj += pulp.lpSum(rota[week, person, role.SHADOW.name] for week in range(num_weeks) for person in people.keys())

    # Introduce a bit of randomisation by assigning each (week,person) pair a random score, and try to optimise the score
    scores = {}
    for week in range(num_weeks):
        scores[week] = {}
        for person in people.keys():
            scores[week][person] = random.randint(0, 10)

    randomise = pulp.lpSum(scores[week][person] * rota[week, person, role.name] for week in range(num_weeks) for person in people.keys() for role in Role)

    prob += obj * 1000000 + randomise

    prob.solve(pulp.solvers.GLPK())
    return rota


def is_assigned(var, week, person, role):
    """Check if someone is assigned for a given role in a given week.
    """

    return pulp.value(var[week, person, role.name]) == 1
