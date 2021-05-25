import collections
import enum
import pulp

from rota import Rota, basic_rota, NoSatisfyingRotaError


# A person who can appear in the rota.  People have no names, as
# 'generate_model' is given a dict 'name -> person'.
Person = collections.namedtuple(
    "Person", ["team", "can_do_inhours_primary", "can_do_inhours_secondary", "can_do_inhours_shadow", "can_do_oncall_primary", "can_do_oncall_secondary", "forbidden_weeks"]
)

# A role
Role = collections.namedtuple("Role", ["n", "inhours", "oncall", "mandatory"])


class Roles(enum.Enum):
    """All the different types of role."""

    PRIMARY = Role(0, True, False, True)
    SECONDARY = Role(1, True, False, True)
    SHADOW = Role(2, True, False, False)
    PRIMARY_ONCALL = Role(3, False, True, True)
    SECONDARY_ONCALL = Role(4, False, True, True)


class Govuk2ndLineRota(Rota):
    """A solved rota."""

    def __init__(self, model, num_weeks, people):
        super().__init__("week", num_weeks, Roles, people)
        self.model = model

    def is_assigned(self, week, person, role):
        return pulp.value(self.model[week, person, role.name]) == 1


def generate_model(
    people,
    num_weeks=2,
    max_inhours_shifts_per_person=1,
    max_oncall_shifts_per_person=3,
    optimise=True,
):
    """Generate the mathematical model of the rota problem."""

    prob, rota, assigned = basic_rota(
        "2ndline rota",
        num_weeks,
        people.keys(),
        [role.name for role in Roles],
        optional_roles=[role.name for role in Roles if not role.value.mandatory],
        personal_leave={p: person.forbidden_weeks for p, person in people.items() if person.forbidden_weeks},
    )

    # ## Constraints

    # A person must:
    for person, p in people.items():
        # [2.1] Not be assigned a role they can't take
        for week in range(num_weeks):
            if not p.can_do_inhours_primary:
                prob += rota[week, person, Roles.PRIMARY.name] == 0
            if not p.can_do_inhours_secondary:
                prob += rota[week, person, Roles.SECONDARY.name] == 0
            if not p.can_do_inhours_shadow:
                prob += rota[week, person, Roles.SHADOW.name] == 0
            if not p.can_do_oncall_primary:
                prob += rota[week, person, Roles.PRIMARY_ONCALL.name] == 0
            if not p.can_do_oncall_secondary:
                prob += rota[week, person, Roles.SECONDARY_ONCALL.name] == 0

        # [2.2] Not be assigned roles in two adjacent weeks
        for week in range(num_weeks):
            if week != 0:
                prob += pulp.lpSum(rota[week, person, role.name] for role in Roles) + pulp.lpSum(rota[week - 1, person, role.name] for role in Roles) <= 1

        # [2.3] Not be assigned more than `max_inhours_shifts_per_person` in-hours roles in total
        prob += pulp.lpSum(rota[week, person, role.name] for week in range(num_weeks) for role in Roles if role.value.inhours) <= max_inhours_shifts_per_person

        # [2.4] Not be assigned more than `max_oncall_shifts_per_person` out-of-hours roles in total
        prob += pulp.lpSum(rota[week, person, role.name] for week in range(num_weeks) for role in Roles if role.value.oncall) <= max_oncall_shifts_per_person

        # [2.5] Not be on in-hours support in the same week that someone else from their team is also on in-hours support
        # [2.6] Not be on in-hours support in the week after someone else from their team is also on in-hours support
        for week in range(num_weeks):
            for person2, p2 in people.items():
                if person == person2:
                    continue
                if p.team != p2.team:
                    continue
                prob += pulp.lpSum(rota[week, person, role.name] for role in Roles if role.value.inhours) + pulp.lpSum(rota[week, person2, role.name] for role in Roles if role.value.inhours) <= 1
                if week != 0:
                    prob += (
                        pulp.lpSum(rota[week, person, role.name] for role in Roles if role.value.inhours) + pulp.lpSum(rota[week - 1, person2, role.name] for role in Roles if role.value.inhours) <= 1
                    )

    # ## Optimisations

    if optimise:
        # [1] Maximise the number of people with assignments
        # This is more important than the other optimisations (which are about reducing weeks which are bad in a fairly minor way) so give it a *100 factor
        obj = pulp.lpSum(assigned[person] for person in people.keys()) * 100

        # [2] Maximise the number of weeks with a shadow
        obj += pulp.lpSum(rota[week, person, Roles.SHADOW.name] for week in range(num_weeks) for person in people.keys())

        prob += obj

    prob.solve(pulp.getSolver("COIN_CMD"))

    if prob.status != pulp.constants.LpStatusOptimal:
        raise NoSatisfyingRotaError()

    return Govuk2ndLineRota(rota, num_weeks, people)
