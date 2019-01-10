import csv
import io

import rota


def generate_rota_csv(num_weeks, people, model):
    """Turn a rota into a CSV.
    """

    out = io.StringIO()

    fieldnames = ['week', 'primary', 'secondary', 'shadow', 'primary_oncall', 'secondary_oncall', 'escalation']
    writer = csv.DictWriter(out, fieldnames=fieldnames)
    writer.writeheader()

    for week in range(num_weeks):
        r = {'week': week + 1}
        for role in rota.Roles:
            for person in people.keys():
                if model(week, person, role):
                    r[role.name.lower()] = person

        # constraint [1.2.3]
        primary   = r['primary']
        secondary = r['secondary']
        if people[primary].num_times_inhours < people[secondary].num_times_inhours:
            r['primary']   = secondary
            r['secondary'] = primary

        # constraint [1.6.3]
        primary_oncall   = r['primary_oncall']
        secondary_oncall = r['secondary_oncall']
        if people[secondary_oncall].num_times_oncall < people[primary_oncall].num_times_oncall:
            r['primary_oncall']   = secondary_oncall
            r['secondary_oncall'] = primary_oncall

        writer.writerow(r)

    return out.getvalue()
