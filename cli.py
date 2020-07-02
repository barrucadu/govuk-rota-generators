#!/usr/bin/env python3

"""
GOV.UK 2ndline Rota Generator

Usage:
  cli.py <file> [--num-weeks=<n>] [--max-in-hours-shifts=<n>] [--max-on-call-shifts=<n>]
  cli.py (-h | --help)

Options:
  -h --help                  Show this screen.
  --num-weeks=<n>            Number of weeks to generate [default: 12].
  --max-in-hours-shifts=<n>  Maximum number of in-hours shifts someone can have [default: 1].
  --max-on-call-shifts=<n>   Maximum number of on-call shifts someone can have [default: 3].
  --leave-start=<n>          First period for the leave/unavailability columns [default: 1].
"""

from docopt import docopt

import csv
import sys

from rota import NoSatisfyingRotaError

import parser
import rota.govuk_2ndline as govuk_2ndline_rota


def print_rota_csv(rota):
    """Turn a rota into a CSV.
    """

    fieldnames = [rota.period_noun]
    for role in rota.roles:
        fieldnames.append(role.name.lower())

    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()

    for period in range(rota.num_periods):
        r = {rota.period_noun: period + 1}
        for role in rota.roles:
            for person in rota.people.keys():
                if rota.is_assigned(period, person, role):
                    r[role.name.lower()] = person

        rota.post_process(r)
        writer.writerow(r)


def parse_csv_or_die(args, parse_row, errors=[], skip=1, **kwargs):
    """Parse the CSV file or print the errors and exit.
    """

    try:
        with open(args['<file>'], 'r') as f:
            people = parser.parse_csv(f, parse_row, skip=skip, **kwargs)
    except KeyError:
        errors.append("<file> is required")
    except FileNotFoundError:
        errors.append(f"'{args['<file>']}' doesn't exist")
    except parser.CSVException as e:
        errors.extend(e.errors)

    if errors:
        for e in errors:
            print(e)
        sys.exit(1)

    return people


def generate_rota(args):
    """Generate and print the GOV.UK 2ndline support rota.
    """

    errors = []

    num_weeks = parser.parse_int(args, '--num-weeks', errors)
    max_inhours_shifts_per_person = parser.parse_int(args, '--max-in-hours-shifts', errors)
    max_oncall_shifts_per_person = parser.parse_int(args, '--max-on-call-shifts', errors)

    people = parse_csv_or_die(args, parser.govuk_2ndline, errors=errors)

    return govuk_2ndline_rota.generate_model(
        people,
        num_weeks=num_weeks,
        max_inhours_shifts_per_person=max_inhours_shifts_per_person,
        max_oncall_shifts_per_person=max_oncall_shifts_per_person
    )


if __name__ == '__main__':
    try:
        args = docopt(__doc__)
        model = generate_rota(args)
        print_rota_csv(model)
    except NoSatisfyingRotaError:
        print("There is no rota meeting the constraints!  Try a shorter rota, or allowing more shifts per person.")
        sys.exit(2)
