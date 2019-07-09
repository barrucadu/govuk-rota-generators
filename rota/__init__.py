import pulp


class NoSatisfyingRotaError(Exception):
    pass


class Rota:
    """A solved rota.
    """

    def __init__(self, period_noun, num_periods, roles, people):
        self.period_noun = period_noun
        self.num_periods = num_periods
        self.roles = roles
        self.people = people


    def is_assigned(self, period, person, role):
        """Check if someone is assigned.
        """

        raise NotImplemented()


    def post_process(self, assignments):
        """Transform a single period's assignments.

        Mutates the parameter.
        """

        pass


def if_then(prob, var_a, k, var_b, var_d):
    """Translate 'if var_a > k then var_b >= 0 else var_b = 0' into ILP constraints.

    'var_d' must be a fresh decision variable.

    See http://www.yzuda.org/Useful_Links/optimization/if-then-else-02.html
    """

    # a number bigger than the number of times someone can actually be on shift
    m = 999

    prob += var_a - k + m * var_d >= 1
    prob += var_b + m * var_d >= 0
    prob += var_a - k <= 0 + m * (1 - var_d)
    prob += var_b <= m * (1 - var_d)


def basic_rota(title, num_periods, person_names, role_names, optional_roles=[], personal_leave={}, sense=pulp.LpMaximize):
    """Generate a basic rota problem that ensures:

    - Each optional role is assigned at most once in each period.
    - Each non-optional role is assigned exactly once in each period.
    - A person is assigned at most one role in each period.
    - A person is not assigned in any period they're on leave for.
    """

    prob = pulp.LpProblem(name=title, sense=pulp.LpMaximize)

    # Model the rota as a [num weeks x num people x num roles] matrix, where rota[week,person,role] == that person has that role for that week.
    rota = pulp.LpVariable.dicts('rota', ((period, person, role) for period in range(num_periods) for person in person_names for role in role_names), cat='Binary')

    # Track whether a person has been assigned
    assigned = pulp.LpVariable.dicts('assigned', person_names, cat='Binary')
    for person in person_names:
        prob += assigned[person] <= pulp.lpSum(rota[period, person, role] for period in range(num_periods) for role in role_names)
        for period in range(num_periods):
            prob += assigned[person] >= pulp.lpSum(rota[period, person, role] for role in role_names)

    # Each optional role is assigned at most once in each period
    # Each non-optional role is assigned exactly once in each period
    for period in range(num_periods):
        for role in role_names:
            if role in optional_roles:
                prob += pulp.lpSum(rota[period, person, role] for person in person_names) <= 1
            else:
                prob += pulp.lpSum(rota[period, person, role] for person in person_names) == 1

    # A person is assigned at most one role in each period
    for person in person_names:
        for period in range(num_periods):
            prob += pulp.lpSum(rota[period, person, role] for role in role_names) <= 1

    # A person is not assigned in any period they're on leave for
    for person, leave_periods in personal_leave.items():
        for period in leave_periods:
            if period < num_periods:
                for role in role_names:
                    prob += rota[period, person, role] == 0

    return prob, rota, assigned
