import collections
import enum
import pulp

from rota import Rota, basic_rota, NoSatisfyingRotaError


# A person who can appear in the rota.  People have no names, as
# 'generate_model' is given a dict 'name -> person'.
Person = collections.namedtuple("Person", ["team", "can_do_inhours", "num_times_inhours", "num_times_shadow", "can_do_oncall", "num_times_oncall", "forbidden_weeks"])

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
    times_inhours_for_primary=3,
    times_shadow_for_secondary=3,
    times_oncall_for_secondary=3,
    max_times_shadow=3,
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

    # In every week:
    for week in range(num_weeks):
        # [2.1.1] Primary must: be able to do in-hours support
        # [2.2.1] Secondary must: be able to do in-hours support
        # [2.3.1] Shadow must: be able to do in-hours support
        # [2.4]   Primary oncall must: be able to do out-of-hours support
        # [2.5.1] Secondary oncall must: be able to do out-of-hours support
        for person, p in people.items():
            for role in Roles:
                if role.value.inhours and not p.can_do_inhours:
                    prob += rota[week, person, role.name] == 0
                if role.value.oncall and not p.can_do_oncall:
                    prob += rota[week, person, role.name] == 0

        # [2.1.2] Primary must: have been on in-hours support at least `times_inhours_for_primary` times
        # [2.2.2] Secondary must: have shadowed at least `times_shadow_for_secondary` times
        # [2.5.2] Secondary oncall must: have done out-of-hours support at least `times_oncall_for_secondary` times
        for person, p in people.items():
            if p.num_times_inhours < times_inhours_for_primary:
                prob += rota[week, person, Roles.PRIMARY.name] == 0
            if p.num_times_shadow < times_shadow_for_secondary:
                prob += rota[week, person, Roles.SECONDARY.name] == 0
            if p.num_times_oncall < times_oncall_for_secondary:
                prob += rota[week, person, Roles.SECONDARY_ONCALL.name] == 0

    # A person must:
    for person, p in people.items():
        # [2.4.2] Not shadow more than `max_times_shadow` times
        if p.num_times_shadow >= max_times_shadow:
            prob += pulp.lpSum(rota[week, person, Roles.SHADOW.name] for week in range(num_weeks)) == 0
        else:
            prob += p.num_times_shadow + pulp.lpSum(rota[week, person, Roles.SHADOW.name] for week in range(num_weeks)) <= max_times_shadow

        # [3.1] Not be assigned roles in two adjacent weeks
        for week in range(num_weeks):
            if week != 0:
                prob += pulp.lpSum(rota[week, person, role.name] for role in Roles) + pulp.lpSum(rota[week - 1, person, role.name] for role in Roles) <= 1

        # [3.2] Not be assigned more than `max_inhours_shifts_per_person` in-hours roles in total
        prob += pulp.lpSum(rota[week, person, role.name] for week in range(num_weeks) for role in Roles if role.value.inhours) <= max_inhours_shifts_per_person

        # [3.3] Not be assigned more than `max_oncall_shifts_per_person` out-of-hours roles in total
        prob += pulp.lpSum(rota[week, person, role.name] for week in range(num_weeks) for role in Roles if role.value.oncall) <= max_oncall_shifts_per_person

        # [3.4] Not be on in-hours support in the same week that someone else from their team is also on in-hours support
        # [3.5] Not be on in-hours support in the week after someone else from their team is also on in-hours support
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
        # [1] Minimise the maximum number of roles-assignments any one person has
        # This is more important than the other optimisations (which are about reducing weeks which are bad in a fairly minor way) so give it a *1000 factor
        obj = pulp.lpSum(assigned[person] for person in people.keys()) * 100

        # [2] Maximise the number of weeks where secondary has been on in-hours support fewer than `times_inhours_for_primary` times
        obj += pulp.lpSum(rota[week, person, Roles.SECONDARY.name] for week in range(num_weeks) for person, p in people.items() if p.num_times_inhours < times_inhours_for_primary)

        # [3] Maximise the number of weeks where primary oncall has been on out-of-hours support fewer than `times_oncall_for_secondary` times
        obj += pulp.lpSum(rota[week, person, Roles.PRIMARY_ONCALL.name] for week in range(num_weeks) for person, p in people.items() if p.num_times_oncall < times_oncall_for_secondary)

        # [4] Maximise the number of weeks with a shadow
        # or: Maximise the number of role assignments; which will have the same effect as the mandatory roles are always assigned
        obj += pulp.lpSum(rota[week, person, role.name] for week in range(num_weeks) for person in people.keys() for role in Roles)

        prob += obj

    prob.solve(pulp.getSolver("COIN_CMD"))

    if prob.status != pulp.constants.LpStatusOptimal:
        raise NoSatisfyingRotaError()

    return Govuk2ndLineRota(rota, num_weeks, people)
