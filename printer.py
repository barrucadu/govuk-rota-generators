import csv
import io


def generate_rota_csv(rota):
    """Turn a rota into a CSV.
    """

    out = io.StringIO()


    fieldnames = [rota.period_noun]
    for role in rota.roles:
        fieldnames.append(role.name.lower())

    writer = csv.DictWriter(out, fieldnames=fieldnames)
    writer.writeheader()

    for period in range(rota.num_periods):
        r = {rota.period_noun: period + 1}
        for role in rota.roles:
            for person in rota.people.keys():
                if rota.is_assigned(period, person, role):
                    r[role.name.lower()] = person

        rota.post_process(r)

        writer.writerow(r)

    return out.getvalue()
