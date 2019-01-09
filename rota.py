import collections
import enum
import pulp
import random
from tabulate import tabulate


class NoSatisfyingRotaError(Exception):
    pass


class SolverError(Exception):
    def __init__(self, dump, week, problem):
        super().__init__(f"Week {week}: {problem}\n{dump}")
        self.dump = dump
        self.week = week
        self.problem = problem


# A person who can appear in the rota.  People have no names, as
# 'generate_model' is given a dict 'name -> person'.
Person = collections.namedtuple('Person', ['team', 'can_do_inhours', 'num_times_inhours', 'num_times_shadow', 'can_do_oncall', 'num_times_oncall', 'can_do_escalations', 'forbidden_weeks'])

# A role
Role = collections.namedtuple('Role', ['n', 'inhours', 'oncall', 'escalation', 'mandatory'])


class Roles(enum.Enum):
    """All the different types of role.
    """

    PRIMARY          = Role(0, True, False, False, True)
    SECONDARY        = Role(1, True, False, False, True)
    SHADOW           = Role(2, True, False, False, False)
    PRIMARY_ONCALL   = Role(3, False, True, False, True)
    SECONDARY_ONCALL = Role(4, False, True, False, True)
    ESCALATION       = Role(5, False, False, True, True)


def is_assigned(var, week, person, role):
    """Check if someone is assigned for a given role in a given week.
    """

    return pulp.value(var[week, person, role.name]) == 1


def get_assignee(var, week, people, role):
    """Find who is assigned to the role, raise 'SolverError' if multiple
    people are.
    """

    out = None
    for person in people.keys():
        if is_assigned(var, week, person, role):
            if out is not None:
                raise SolverError(week, f"Multiple assignments to {role.name}")
            out = person
    return out


def dump_ilp(num_weeks, people, rota):
    """Generate a textual dump of the variable assignments.
    """

    dump = []
    for week in range(num_weeks):
        assignments = {role: [] for role in Roles}
        for role in Roles:
            for person in people:
                if is_assigned(rota, week, person, role):
                    assignments[role].append(person)
        dump.append([week, assignments[Roles.PRIMARY], assignments[Roles.SECONDARY], assignments[Roles.SHADOW], assignments[Roles.PRIMARY_ONCALL], assignments[Roles.SECONDARY_ONCALL], assignments[Roles.ESCALATION]])

    return tabulate(dump, ["week", "primary", "secondary", "shadow", "primary_oncall", "secondary_oncall", "escalation"])


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


def validate_model(num_weeks, max_inhours_shifts_per_person, max_oncall_shifts_per_person, max_escalation_shifts_per_person, people, rota):
    """Validate the rota meets the constraints - as Cbc returned an invalid one.
    """

    dump = dump_ilp(num_weeks, people.keys(), rota)

    times_inhours = {person: p.num_times_inhours for person, p in people.items()}
    times_shadow  = {person: p.num_times_shadow  for person, p in people.items()}
    times_oncall  = {person: p.num_times_oncall  for person, p in people.items()}

    assignments_inhours    = {person: 0 for person in people.keys()}
    assignments_oncall     = {person: 0 for person in people.keys()}
    assignments_escalation = {person: 0 for person in people.keys()}

    previous = []

    for week in range(num_weeks):
        primary   = get_assignee(rota, week, people, Roles.PRIMARY)
        secondary = get_assignee(rota, week, people, Roles.SECONDARY)
        shadow    = get_assignee(rota, week, people, Roles.SHADOW)
        primary_oncall   = get_assignee(rota, week, people, Roles.PRIMARY_ONCALL)
        secondary_oncall = get_assignee(rota, week, people, Roles.SECONDARY_ONCALL)
        escalation = get_assignee(rota, week, people, Roles.ESCALATION)

        # 1.1 - just assume that this means there is no rota which meets the constraints
        if None in [primary, secondary, primary_oncall, secondary_oncall, escalation]:
            raise NoSatisfyingRotaError()
        # 1.2.1
        if not people[primary].can_do_inhours:
            raise SolverError(dump, week, "primary cannot do in-hours support")
        # 1.2.2
        if not times_inhours[primary] >= 3:
            raise SolverError(dump, week, "primary is not experienced enough")
        # 1.2.3
        if not people[primary].num_times_inhours >= people[secondary].num_times_inhours:
            raise SolverError(dump, week, "primary is less experienced than secondary")
        # 1.3.1
        if not people[secondary].can_do_inhours:
            raise SolverError(dump, week, "secondary cannot do in-hours support")
        # 1.3.2
        if not times_shadow[secondary] >= 2:
            raise SolverError(dump, week, "secondary is not experienced enough")
        if shadow is not None:
            # 1.4.1
            if not people[shadow].can_do_inhours:
                raise SolverError(dump, week, "shadow cannot do in-hours support")
            # 1.4.2
            if not times_shadow[shadow] <= 2:
                raise SolverError(dump, week, "shadow has shadowed too many times")
        # 1.5.1
        if not people[primary_oncall].can_do_oncall:
            raise SolverError(dump, week, "primary oncall cannot do out-of-hours support")
        # 1.6.1
        if not people[secondary_oncall].can_do_oncall:
            raise SolverError(dump, week, "secondary oncall cannot do out-of-hours support")
        # 1.6.2
        if not times_oncall[secondary_oncall] >= 3:
            raise SolverError(dump, week, "secondary oncall is not experienced enough")
        # 1.6.3
        if not people[secondary_oncall].num_times_oncall >= people[primary_oncall].num_times_oncall:
            raise SolverError(dump, week, "secondary oncall is less experienced than primary oncall")
        # 1.7
        if not people[escalation].can_do_escalations:
            raise SolverError(dump, week, "escalations cannot be on escalations")

        # 2.1
        if primary in [secondary, shadow, primary_oncall, secondary_oncall]:
            raise SolverError(dump, week, f"{primary} has multiple assignments")
        if secondary in [primary, shadow, primary_oncall, secondary_oncall]:
            raise SolverError(dump, week, f"{secondary} has multiple assignments")
        if shadow in [primary, secondary, primary_oncall, secondary_oncall]:
            raise SolverError(dump, week, f"{shadow} has multiple assignments")
        if primary_oncall in [primary, secondary, shadow, secondary_oncall]:
            raise SolverError(dump, week, f"{primary_oncall} has multiple assignments")
        if secondary_oncall in [primary, secondary, shadow, primary_oncall]:
            raise SolverError(dump, week, f"{secondary_oncall} has multiple assignments")

        # 2.2
        if primary in previous:
            raise SolverError(dump, week, f"{primary} has assignment in previous week")
        if secondary in previous:
            raise SolverError(dump, week, f"{secondary} has assignment in previous week")
        if shadow is not None and shadow in previous:
            raise SolverError(dump, week, f"{shadow} has assignment in previous week")
        if primary_oncall in previous:
            raise SolverError(dump, week, f"{primary_oncall} has assignment in previous week")
        if secondary_oncall in previous:
            raise SolverError(dump, week, f"{secondary_oncal} has assignment in previous week")

        times_inhours[primary]         = times_inhours[primary] + 1
        times_inhours[secondary]       = times_inhours[secondary] + 1
        times_oncall[primary_oncall]   = times_oncall[primary_oncall] + 1
        times_oncall[secondary_oncall] = times_oncall[secondary_oncall] + 1

        assignments_inhours[primary]         = assignments_inhours[primary] + 1
        assignments_inhours[secondary]       = assignments_inhours[secondary] + 1
        assignments_oncall[primary_oncall]   = assignments_oncall[primary_oncall] + 1
        assignments_oncall[secondary_oncall] = assignments_oncall[secondary_oncall] + 1
        assignments_escalation[escalation]   = assignments_escalation[escalation] + 1

        if shadow is not None:
            times_shadow[shadow]        = times_shadow[shadow] + 1
            assignments_inhours[shadow] = assignments_inhours[shadow] + 1

        previous = [primary, secondary, shadow, primary_oncall, secondary_oncall]

        for person, p in people.items():
            # 2.3
            if week in p.forbidden_weeks:
                if person in [primary, secondary, shadow, primary_oncall, secondary_oncall]:
                    raise SolverError(dump, week, f"{person} has assignment in forbidden week")
            # 2.4
            if assignments_inhours[person] > max_inhours_shifts_per_person:
                raise SolverError(dump, week, f"{person} has too many in-hours assignments")
            # 2.5
            if assignments_oncall[person] > max_oncall_shifts_per_person:
                raise SolverError(dump, week, f"{person} has too many in-hours assignments")
            # 2.6
            if assignments_escalation[person] > max_escalation_shifts_per_person:
                raise SolverError(dump, week, f"{person} has too many escalation assignments")

        # 2.7
        if len(set(people[person].team for person in [primary, secondary, shadow] if person is not None)) != (2 if shadow is None else 3):
            raise SolverError(dump, week, "multiple in-hours people are on the same team")



def generate_model(num_weeks, max_inhours_shifts_per_person, max_oncall_shifts_per_person, max_escalation_shifts_per_person, people):
    """Generate the mathematical model of the rota problem.
    """

    prob = pulp.LpProblem(name='2ndline rota', sense=pulp.LpMaximize)

    # Model the rota as a [num weeks x num people x num roles] matrix, where rota[week,person,role] == that person has that role for that week.
    rota = pulp.LpVariable.dicts('rota', ((week, person, role.name) for week in range(num_weeks) for person in people.keys() for role in Roles), cat='Binary')

    # Auxilliary variable to track if someone is assigned
    assigned = pulp.LpVariable.dicts('assigned', people.keys(), cat='Binary')

    # Auxilliary variables to track the number of times someone has shadowed, been a non-shadow in-hours, or been on-call
    times_shadow  = pulp.LpVariable.dicts('times_shadow',  ((week, person) for week in range(num_weeks) for person in people.keys()), cat='Integer')
    times_inhours = pulp.LpVariable.dicts('times_inhours', ((week, person) for week in range(num_weeks) for person in people.keys()), cat='Integer')
    times_oncall  = pulp.LpVariable.dicts('times_oncall',  ((week, person) for week in range(num_weeks) for person in people.keys()), cat='Integer')

    # Auxilliary decision variable for if-then constructs
    # http://www.yzuda.org/Useful_Links/optimization/if-then-else-02.html
    d = pulp.LpVariable.dicts('d', ((week, person, role.name) for week in range(num_weeks) for person in people.keys() for role in Roles), cat='Binary')

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
                prob += times_shadow[week, person]  == times_shadow[week - 1, person]  + rota[week - 1, person, Roles.SHADOW.name]
                prob += times_inhours[week, person] == times_inhours[week - 1, person] + rota[week - 1, person, Roles.PRIMARY.name]        + rota[week - 1, person, Roles.SECONDARY.name]
                prob += times_oncall[week, person]  == times_oncall[week - 1, person]  + rota[week - 1, person, Roles.PRIMARY_ONCALL.name] + rota[week - 1, person, Roles.SECONDARY_ONCALL.name]

        # [1.1] Each role must be assigned to exactly one person, except shadow which may be unassigned.
        for role in Roles:
            if role.value.mandatory:
                prob += pulp.lpSum(rota[week, person, role.name] for person in people.keys()) == 1
            else:
                prob += pulp.lpSum(rota[week, person, role.name] for person in people.keys()) <= 1

        # [1.2.1] Primary must: be able to do in-hours support
        # [1.3.1] Secondary must: be able to do in-hours support
        # [1.4.1] Shadow must: be able to do in-hours support
        # [1.5.1] Primary oncall must: be able to do out-of-hours support
        # [1.6.1] Secondary oncall must: be able to do out-of-hours support
        # [1.7]   Escalation must: be able to do escalatons
        for person, p in people.items():
            for role in Roles:
                if role.value.inhours:
                    prob += rota[week, person, role.name] <= (1 if p.can_do_inhours     else 0)
                if role.value.oncall:
                    prob += rota[week, person, role.name] <= (1 if p.can_do_oncall      else 0)
                if role.value.escalation:
                    prob += rota[week, person, role.name] <= (1 if p.can_do_escalations else 0)

        # [1.2.2] Primary must: have been on in-hours support at least 3 times
        # [1.3.2] Secondary must: have shadowed at least twice
        # [1.6.2] Secondary oncall must: have done out-of-hours support at least 3 times
        for person in people.keys():
            if_then(prob, times_inhours[week, person], 2, rota[week, person, Roles.PRIMARY.name],        d[week, person, Roles.PRIMARY.name])
            if_then(prob, times_shadow[week, person],  1, rota[week, person, Roles.SECONDARY.name],      d[week, person, Roles.SECONDARY.name])
            if_then(prob, times_oncall[week, person],  2, rota[week, person, Roles.SECONDARY_ONCALL.name], d[week, person, Roles.SECONDARY_ONCALL.name])

        # [1.2.3] Ensure the primary is at least as experienced as the secondary
        prob += pulp.lpSum(rota[week, person, Roles.PRIMARY.name] * p.num_times_inhours for person, p in people.items()) >= pulp.lpSum(rota[week, person, Roles.SECONDARY.name] * p.num_times_inhours for person, p in people.items())

        # [1.6.3] Ensure the secondary oncall is at least as experienced as the primary oncall
        prob += pulp.lpSum(rota[week, person, Roles.SECONDARY_ONCALL.name] * p.num_times_oncall for person, p in people.items()) >= pulp.lpSum(rota[week, person, Roles.PRIMARY_ONCALL.name] * p.num_times_oncall for person, p in people.items())

    # A person must:
    for person, p in people.items():
        # Constrain 'assigned' auxilliary variable.
        for week in range(num_weeks):
            prob += assigned[person] >= pulp.lpSum(rota[week, person, role.name] for role in Roles)

        # [1.4.2] Not shadow more than twice
        prob += times_shadow[num_weeks - 1, person] <= 2

        # [2.1] Not be assigned more than one role in the same week
        for week in range(num_weeks):
            prob += pulp.lpSum(rota[week, person, role.name] for role in Roles) <= 1

        # [2.2] Not be assigned roles in two adjacent weeks
        for week in range(num_weeks):
            if week == num_weeks - 1:
                break
            prob += pulp.lpSum(rota[week, person, role.name] for role in Roles) + pulp.lpSum(rota[week + 1, person, role.name] for role in Roles) <= 1

        # [2.3] Not be assigned a role in a week they cannot do
        for forbidden_week in p.forbidden_weeks:
            prob += pulp.lpSum(rota[forbidden_week, person, role.name] for role in Roles) == 0

        # [2.4] Not be assigned more than `max_inhours_shifts_per_person` in-hours roles in total
        prob += pulp.lpSum(rota[week, person, role.name] for week in range(num_weeks) for role in Roles if role.value.inhours) <= max_inhours_shifts_per_person

        # [2.5] Not be assigned more than `max_oncall_shifts_per_person` out-of-hours roles in total
        prob += pulp.lpSum(rota[week, person, role.name] for week in range(num_weeks) for role in Roles if role.value.oncall) <= max_oncall_shifts_per_person

        # [2.6] Not be assigned more than `max_escalation_shifts_per_person` escalation roles in total
        prob += pulp.lpSum(rota[week, person, role.name] for week in range(num_weeks) for role in Roles if role.value.escalation) <= max_escalation_shifts_per_person

        # [2.7] Not be on in-hours support in the same week that someone else from their team is also on in-hours support
        for week in range(num_weeks):
            for person2, p2 in people.items():
                if person == person2:
                    continue
                if p.team != p2.team:
                    continue
                prob += pulp.lpSum(rota[week, person, role.name] for role in Roles if role.value.inhours) + pulp.lpSum(rota[week, person2, role.name] for role in Roles if role.value.inhours) <= 1

    ### Optimisations

    # [1] Minimise the maximum number of roles-assignments any one person has
    # or: Maximise the number of people with assignments
    # This is more important than the other optimisations (which are about reducing weeks which are bad in a fairly minor way) so give it a *1000 factor
    obj = pulp.lpSum(assigned[person] for person in people.keys()) * 1000

    # [2] Maximise the number of weeks where secondary has been on in-hours support fewer than 3 times
    obj += pulp.lpSum(rota[week, person, Roles.SECONDARY.name] for week in range(num_weeks) for person, p in people.items() if p.num_times_inhours < 3)

    # [3] Maximise the number of weeks where primary oncall has been on out-of-hours support fewer than 3 times
    obj += pulp.lpSum(rota[week, person, Roles.PRIMARY_ONCALL.name] for week in range(num_weeks) for person, p in people.items() if p.num_times_oncall < 3)

    # [4] Maximise the number of weeks with a shadow
    # or: Maximise the number of role assignments; which will have the same effect as the mandatory roles are always assigned
    obj += pulp.lpSum(rota[week, person, role.name] for week in range(num_weeks) for person in people.keys() for role in Roles)

    # Introduce a bit of randomisation by assigning each (week,person) pair a random score, and try to optimise the score
    scores = {}
    for week in range(num_weeks):
        scores[week] = {}
        for person in people.keys():
            scores[week][person] = random.randint(0, 10)

    randomise = pulp.lpSum(scores[week][person] * rota[week, person, role.name] for week in range(num_weeks) for person in people.keys() for role in Roles)

    prob += obj * 1000000 + randomise

    prob.solve(pulp.solvers.GLPK_CMD(options=['--tmlim', '30']))
    validate_model(num_weeks, max_inhours_shifts_per_person, max_oncall_shifts_per_person, max_escalation_shifts_per_person, people, rota)
    return rota
