import csv
import io

import rota


class RotaException(Exception):
    pass


def generate_rota_csv(num_weeks, persons, var):
    """Turn a rota into a CSV.
    """

    out = io.StringIO()

    fieldnames = ['week', 'primary', 'secondary', 'shadow', 'primary_oncall', 'secondary_oncall']
    writer = csv.DictWriter(out, fieldnames=fieldnames)
    writer.writeheader()

    for week in range(num_weeks):
        r = {'week': week + 1}
        for role in rota.Role:
            for person in persons:
                if rota.is_assigned(var, week, person, role):
                    r[role.name.lower()] = person
        # if there isn't a legal rota, there will be no assignments so
        # just check one
        if 'primary' not in r:
            raise RotaException('Could not generate a legal rota!')
        writer.writerow(r)

    return out.getvalue()
