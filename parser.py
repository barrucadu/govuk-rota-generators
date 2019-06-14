import csv

import rota


class CSVException(Exception):
    def __init__(self, errors):
        super().__init__('Encountered errors parsing the CSV')
        self.errors = errors


def to_bool(s):
    """A stricter boolification function than 'bool'.
    """

    true_strings = ['true', 'yes', 'y', '1']
    false_strings = ['false', 'no', 'n', '0']

    if s.lower() in true_strings:
        return True
    if s.lower() in false_strings:
        return False

    raise ValueError(f"String '{s} not in {true_strings} or {false_strings}")


def parse_csv_row(rn, row):
    """Parse a row from the CSV, accumulating errors.
    """

    errors = []

    if len(row) != 8:
        errors.append(f"Row {rn}: should have 8 elements")
        raise CSVException(errors)

    person = row[0]
    team = row[1]
    can_do_inhours_str = row[2]
    num_times_inhours_str = row[3]
    num_times_shadow_str = row[4]
    can_do_oncall_str = row[5]
    num_times_oncall_str = row[6]
    forbidden_weeks_str = row[7]

    try:
        can_do_inhours = to_bool(can_do_inhours_str)
    except ValueError:
        errors.append(f"Row {rn}: 'can_do_inhours' field should be a boolean")

    try:
        num_times_inhours = int(num_times_inhours_str)
    except ValueError:
        errors.append(f"Row {rn}: 'num_times_inhours' field should be an integer")

    try:
        num_times_shadow = int(num_times_shadow_str)
    except ValueError:
        errors.append(f"Row {rn}: 'num_times_shadow' field should be an integer")

    try:
        can_do_oncall = to_bool(can_do_oncall_str)
    except ValueError:
        errors.append(f"Row {rn}: 'can_do_oncall' field should be a boolean")

    try:
        num_times_oncall = int(num_times_oncall_str)
    except ValueError:
        errors.append(f"Row {rn}: 'num_times_oncall' field should be an integer")

    try:
        forbidden_weeks = [int(n) - 1 for n in forbidden_weeks_str.split(',') if n != '']
    except ValueError:
        errors.append(f"Row {rn}: 'forbidden_weeks' field should be a comma-separated list of weeks")

    if errors:
        raise CSVException(errors)

    return person, rota.Person(
        team=team.strip().lower(),
        can_do_inhours=can_do_inhours,
        num_times_inhours=num_times_inhours,
        num_times_shadow=num_times_shadow,
        can_do_oncall=can_do_oncall,
        num_times_oncall=num_times_oncall,
        forbidden_weeks=forbidden_weeks
    )



def people_from_csv(csvfile):
    """Parse the people csv, accumulating errors.
    """

    reader = csv.reader(csvfile)
    header = True
    people = {}
    errors = []
    rn = 0
    for row in reader:
        if header:
            header = False
        else:
            try:
                person, p = parse_csv_row(rn, row)
                people[person] = p
            except CSVException as e:
                errors.extend(e.errors)
        rn += 1

    if errors:
        raise CSVException(errors)

    return people


def parse_int(d, field, errors):
    """Parse 'd[field]' as an int, or append an error to 'errors'.
    """

    try:
        return int(d[field])
    except KeyError:
        errors.append(f"'{field}' is required")
    except ValueError:
        errors.append(f"'{field}' must be a number")
