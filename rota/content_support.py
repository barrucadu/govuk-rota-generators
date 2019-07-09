import collections
import enum
import itertools
import multiprocessing
import pulp
import random
import sys

from rota import *


Person = collections.namedtuple('Person', ['team', 'role', 'can_do_2i', 'can_do_cr', 'can_do_2ndline', 'forbidden_periods'])

Role = collections.namedtuple('Role', ['n', 'is_2i', 'is_cr', 'is_2ndline'])

class Roles(enum.Enum):
    """All the different types of role.
    """

    A_2I      = Role(1, True, False, False)
    B_2I      = Role(2, True, False, False)
    CR        = Role(3, False, True, False)
    A_2NDLINE = Role(4, False, False, True)
    B_2NDLINE = Role(5, False, False, True)


class ContentSupportRota(Rota):
    """A solved rota.
    """

    def __init__(self, model, num_periods, people):
        super().__init__('day', num_periods, Roles, people)
        self.model = model


    def is_assigned(self, period, person, role):
        return pulp.value(self.model[period, person, role.name]) == 1


def __generate_model(args):
    """Internal version of 'generate_model' which is run in parallel.
    """

    if args is None:
        return None

    people, num_weeks, scd_period_limit, other_period_limit, product_people_limit, optimise = args
    print(f'Trying scd_period_limit={scd_period_limit} other_period_limit={other_period_limit} product_people_limit={product_people_limit}...', file=sys.stderr)

    num_periods = num_weeks * 5

    prob, rota, assigned = basic_rota('content support rota', num_periods, people.keys(), [role.name for role in Roles],
        personal_leave={p: person.forbidden_periods for p, person in people.items() if person.forbidden_periods},
    )

    # In every period:
    for period in range(num_periods):
        # [1.1] 2i_a must be able to do 2i
        # [1.2] 2i_b must be able to do 2i
        # [1.3] cr must be able to do cr
        # [1.4] 2ndline_a must be able to do 2ndline
        # [1.5] 2ndline_b must be able to do 2ndline
        for person, p in people.items():
            for role in Roles:
                if role.value.is_2i and not p.can_do_2i:
                    prob += rota[period, person, role.name] == 0
                if role.value.is_cr and not p.can_do_cr:
                    prob += rota[period, person, role.name] == 0
                if role.value.is_2ndline and not p.can_do_2ndline:
                    prob += rota[period, person, role.name] == 0

        # [1.6] 2i_a must not be on the same team as 2i_b
        for name1, p1 in people.items():
            if not p1.can_do_2i:
                continue
            for name2, p2 in people.items():
                if p1 == p2 or not p2.can_do_2i:
                    continue
                if p1.team == p2.team:
                    # person 1 could be 2i_a or 2i_b (and same for person 2)
                    prob += rota[period, name1, Roles.A_2I.name] + rota[period, name2, Roles.B_2I.name] <= 1
                    prob += rota[period, name1, Roles.B_2I.name] + rota[period, name2, Roles.A_2I.name] <= 1

    # A person must:
    for person, p in people.items():
        if p.team == 'product':
            # [2.1] not be assigned multiple roles in the same 10 working day period if they are on a product team
            for period_start in range(num_periods):
                period_stop = min(period_start + 10, num_periods - 1) + 1 # inclusive
                prob += pulp.lpSum(rota[period, person, role.name] for period in range(period_start, period_stop) for role in Roles) <= 1
        else:
            # [SC1&2] only be on the rota once every <period_limit> working days (excluding 2ndline)
            period_limit = scd_period_limit if p.role == 'scd' else other_period_limit
            for period_start in range(num_periods):
                period_stop = min(period_start + period_limit, num_periods - 1) + 1 # inclusive
                prob += pulp.lpSum(rota[period, person, role.name] for period in range(period_start, period_stop) for role in Roles if not role.value.is_2ndline) <= 1

        # [2.2] not be assigned roles on adjacent days
        for period in range(num_periods - 1):
            prob += pulp.lpSum(rota[period, person, role.name] for role in Roles) + pulp.lpSum(rota[period + 1, person, role.name] for role in Roles) <= 1

    # [SC3] <product_people_limit> people on a product team will be in the rota
    prob += pulp.lpSum(assigned[person] for person, p in people.items() if p.team == 'product') <= product_people_limit

    if optimise:
        # [1] Minimise the maximum number of roles-assignments any one person has
        # or: Maximise the number of people with assignments
        obj = pulp.lpSum(assigned[person] for person in people.keys()) * 100

        # [2] 2ndline_a and 2ndline_b are on different teams
        # ?

        # [3] Part-time people are scheduled pro-rata (but not necessarily excluded!)
        # ?

        # Introduce a bit of randomisation - I feel there should be a
        # way to do this which doesn't add arbitrary hardness to the
        # problem...
        randomise = pulp.lpSum(random.randint(0, 1) * rota[period, person, role.name] for period in range(num_periods) for person in people.keys() for role in Roles)

        prob += obj * 100 + randomise

    prob.solve(pulp.solvers.COIN_CMD())

    if prob.status != pulp.constants.LpStatusOptimal:
        print('...failed', file=sys.stderr)
        return None

    print('...ok!', file=sys.stderr)
    return ContentSupportRota(rota, num_periods, people)


def chunks_of(iterable, n):
    """Generate chunks of the given length, pads with None if it's not an exact fit.

    From https://docs.python.org/3/library/itertools.html
    """

    return itertools.zip_longest(*([iter(iterable)] * n))


def generate_model(
        people,
        num_weeks=12,
        soft_scd_period_limit=5,
        soft_other_period_limit=9,
        soft_product_people_limit=1,
        optimise=True,
        num_cores=4,
):
    params = []

    soft_scd_period_limit_bound = 1
    soft_other_period_limit_bound = 1
    soft_product_people_limit_bound = len([p for p in people.values() if p.team == 'product'])

    reduction = ['soft_scd_period_limit', 'soft_other_period_limit', 'soft_product_people_limit']
    random.shuffle(reduction)
    while reduction:
        params.append((people, num_weeks, soft_scd_period_limit, soft_other_period_limit, soft_product_people_limit, optimise))
        if reduction[0] == 'soft_scd_period_limit':
            soft_scd_period_limit -= 1
        elif reduction[0] == 'soft_other_period_limit':
            soft_other_period_limit -= 1
        elif reduction[0] == 'soft_product_people_limit':
            soft_product_people_limit += 1
        del reduction[0]
        if reduction == []:
            if soft_scd_period_limit > soft_scd_period_limit_bound:
                reduction.append('soft_scd_period_limit')
            if soft_other_period_limit > soft_other_period_limit_bound:
                reduction.append('soft_other_period_limit')
            if soft_product_people_limit < soft_product_people_limit_bound:
                reduction.append('soft_product_people_limit')
            random.shuffle(reduction)

    with multiprocessing.Pool() as p:
        for ps in chunks_of(params, num_cores):
            for result in p.imap_unordered(__generate_model, ps):
                if result is not None:
                    p.terminate()
                    return result

    raise NoSatisfyingRotaError()
