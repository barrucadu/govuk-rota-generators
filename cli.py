#!/usr/bin/env python3

"""
GOV.UK 2ndline Rota Generator

Usage:
  cli.py [--num-weeks=<n>] [--max-in-hours-shifts=<n>] [--max-on-call-shifts=<n>] <file>
  cli.py (-h | --help)

Options:
  -h --help                  Show this screen.
  --num-weeks=<n>            Number of weeks to generate [default: 12].
  --max-in-hours-shifts=<n>  Maximum number of in-hours shifts someone can have [default: 1].
  --max-on-call-shifts=<n>   Maximum number of on-call shifts someone can have [default: 3].
"""

from docopt import docopt
import sys

import parser
import printer
import rota


def generate_rota(args):
    errors = []

    try:
        num_weeks = int(args['--num-weeks'])
    except KeyError:
        errors.append("--num-weeks is required")
    except ValueError:
        errors.append("--num-weeks must be a number")

    try:
        max_inhours_shifts_per_person = int(args['--max-in-hours-shifts'])
    except KeyError:
        errors.append("--max-in-hours-shifts is required")
    except ValueError:
        errors.append("--max-in-hours-shifts must be a number")

    try:
        max_oncall_shifts_per_person = int(args['--max-on-call-shifts'])
    except KeyError:
        errors.append("--max-on-call-shifts is required")
    except ValueError:
        errors.append("--max-on-call-shifts must be a number")

    try:
        with open(args['<file>'], 'r') as f:
            people = parser.people_from_csv(f)
    except KeyError:
        errors.append("<file> is required")
    except parser.CSVException as e:
        errors.extend(e.errors)

    if errors:
        for e in errors:
            print(e)
        sys.exit(1)

    try:
        model = rota.generate_model(num_weeks, max_inhours_shifts_per_person, max_oncall_shifts_per_person, people)
    except rota.NoSatisfyingRotaError:
        print("There is no rota meeting the constraints!  Try a shorter rota, or allowing more shifts per person.")
        sys.exit(2)
    except rota.SolverError as e:
        print(str(e))
        sys.exit(3)

    rota_csv_string = printer.generate_rota_csv(num_weeks, people, model)
    print(rota_csv_string)


if __name__ == '__main__':
    generate_rota(docopt(__doc__))
