import csv
import flask
import io
import rota

app = flask.Flask(__name__)


class CSVException(Exception):
    def __init__(self, errors):
        super().__init__('Encountered errors parsing the CSV')
        self.errors = errors


class RotaException(Exception):
    pass


def to_bool(s):
    true_strings = ['true', 'yes', 'y', '1']
    false_strings = ['false', 'no', 'n', '0']

    if s.lower() in true_strings:
        return True
    if s.lower() in false_strings:
        return False

    raise ValueError(f"String '{s} not in {true_strings} or {false_strings}")


def parse_csv_row(rn, row):
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
        team = team,
        can_do_inhours = can_do_inhours,
        num_times_inhours = num_times_inhours,
        num_times_shadow = num_times_shadow,
        can_do_oncall = can_do_oncall,
        num_times_oncall = num_times_oncall,
        forbidden_weeks = forbidden_weeks
    )



def people_from_csv(csv_bytes):
    """Parse the people csv.
    """

    reader = csv.reader(io.StringIO(csv_bytes.stream.read().decode("UTF8"), newline=None))
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


def generate_rota_csv(num_weeks, persons, var):
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


@app.route('/', methods=['GET'])
def index():
    return flask.render_template('index.html')


@app.route('/rota', methods=['POST'])
def generate_rota():
    form_errors = []
    csv_errors = []

    try:
        num_weeks = int(flask.request.form['num_weeks'])
    except KeyError:
        form_errors.append("Field 'num_weeks' is expected to exist")
    except ValueError:
        form_errors.append("Field 'num_weeks' is expected to be a number")

    try:
        max_inhours_shifts_per_person = int(flask.request.form['max_inhours_shifts_per_person'])
    except KeyError:
        form_errors.append("Field 'max_inhours_shifts_per_person' is expected to exist")
    except ValueError:
        form_errors.append("Field 'max_inhours_shifts_per_person' is expected to be a number")

    try:
        max_oncall_shifts_per_person = int(flask.request.form['max_oncall_shifts_per_person'])
    except KeyError:
        form_errors.append("Field 'max_oncall_shifts_per_person' is expected to exist")
    except ValueError:
        form_errors.append("Field 'max_oncall_shifts_per_person' is expected to be a number")

    try:
        people = people_from_csv(flask.request.files['people'])
    except KeyError:
        form_errors.append("Field 'people' is expected to exist")
    except CSVException as e:
        csv_errors = e.errors

    if form_errors or csv_errors:
        return flask.render_template('error.html', form_errors=form_errors, csv_errors=csv_errors)

    rota_vars = rota.generate_model(num_weeks, max_inhours_shifts_per_person, max_oncall_shifts_per_person, people)

    try:
        rota_csv_string = generate_rota_csv(num_weeks, people.keys(), rota_vars)
        return flask.Response(rota_csv_string, mimetype = 'text/plain')
    except RotaException as e:
        return flask.render_template('error.html', message=str(e))
