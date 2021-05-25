import csv

import rota.govuk_2ndline as govuk_2ndline_rota


class CSVException(Exception):
    def __init__(self, errors):
        super().__init__("Encountered errors parsing the CSV")
        self.errors = errors


def to_bool(s):
    """A stricter boolification function than 'bool'."""

    true_strings = ["true", "yes", "y", "1"]
    false_strings = ["false", "no", "n", "0"]

    if s.lower() in true_strings:
        return True
    if s.lower() in false_strings:
        return False

    raise ValueError(f"String '{s} not in {true_strings} or {false_strings}")


def govuk_2ndline(rn, row):
    """Parse a row from the CSV, accumulating errors."""

    errors = []

    if len(row) != 8:
        errors.append(f"Row {rn}: should have 8 elements (got {len(row)})")
        raise CSVException(errors)

    person = row[0].strip()
    team = row[1].lower().strip()
    can_do_inhours_primary_str = row[2].strip()
    can_do_inhours_secondary_str = row[3].strip()
    can_do_inhours_shadow_str = row[4].strip()
    can_do_oncall_primary_str = row[5].strip()
    can_do_oncall_secondary_str = row[6].strip()
    forbidden_weeks_str = row[7].strip()

    try:
        can_do_inhours_primary = to_bool(can_do_inhours_primary_str)
    except ValueError:
        errors.append(f"Row {rn}: 'can_do_inhours_primary' field should be a boolean (got '{can_do_inhours_primary_str}')")

    try:
        can_do_inhours_secondary = to_bool(can_do_inhours_secondary_str)
    except ValueError:
        errors.append(f"Row {rn}: 'can_do_inhours_secondary' field should be a boolean (got '{can_do_inhours_secondary_str}')")

    try:
        can_do_inhours_shadow = to_bool(can_do_inhours_shadow_str)
    except ValueError:
        errors.append(f"Row {rn}: 'can_do_inhours_shadow' field should be a boolean (got '{can_do_inhours_shadow_str}')")

    try:
        can_do_oncall_primary = to_bool(can_do_oncall_primary_str)
    except ValueError:
        errors.append(f"Row {rn}: 'can_do_oncall_primary' field should be a boolean (got '{can_do_oncall_primary_str}')")

    try:
        can_do_oncall_secondary = to_bool(can_do_oncall_secondary_str)
    except ValueError:
        errors.append(f"Row {rn}: 'can_do_oncall_secondary' field should be a boolean (got '{can_do_oncall_secondary_str}')")

    try:
        forbidden_weeks = [int(n) - 1 for n in forbidden_weeks_str.split(",") if n != ""]
    except ValueError:
        errors.append(f"Row {rn}: 'forbidden_weeks' field should be a comma-separated list of weeks (got '{forbidden_weeks_str}')")

    if errors:
        raise CSVException(errors)

    return {
        person: govuk_2ndline_rota.Person(
            team=team,
            can_do_inhours_primary=can_do_inhours_primary,
            can_do_inhours_secondary=can_do_inhours_secondary,
            can_do_inhours_shadow=can_do_inhours_shadow,
            can_do_oncall_primary=can_do_oncall_primary,
            can_do_oncall_secondary=can_do_oncall_secondary,
            forbidden_weeks=forbidden_weeks,
        )
    }


def parse_csv(csvfile, parse_row, skip=1, **kwargs):
    """Parse the people csv, accumulating errors."""

    reader = csv.reader(csvfile)
    people = {}
    errors = []
    rn = 0
    for row in reader:
        rn += 1
        if skip > 0:
            skip -= 1
            continue
        try:
            for person, p in parse_row(rn, row, **kwargs).items():
                people[person] = p
        except CSVException as e:
            errors.extend(e.errors)

    if errors:
        raise CSVException(errors)

    return people


def parse_int(d, field, errors):
    """Parse 'd[field]' as an int, or append an error to 'errors'."""

    try:
        return int(d[field])
    except KeyError:
        errors.append(f"'{field}' is required")
    except ValueError:
        errors.append(f"'{field}' must be a number")
