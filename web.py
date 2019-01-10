import flask
import io

import parser
import printer
import rota

app = flask.Flask(__name__)


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
        max_escalation_shifts_per_person = int(flask.request.form['max_escalation_shifts_per_person'])
    except KeyError:
        form_errors.append("Field 'max_escalation_shifts_per_person' is expected to exist")
    except ValueError:
        form_errors.append("Field 'max_escalation_shifts_per_person' is expected to be a number")

    try:
        csv_bytes = flask.request.files['people']
        people = parser.people_from_csv(io.StringIO(csv_bytes.stream.read().decode("UTF8"), newline=None))
    except KeyError:
        form_errors.append("Field 'people' is expected to exist")
    except parser.CSVException as e:
        csv_errors = e.errors

    if form_errors or csv_errors:
        return flask.render_template('error.html', form_errors=form_errors, csv_errors=csv_errors)

    try:
        model = rota.generate_model(num_weeks, max_inhours_shifts_per_person, max_oncall_shifts_per_person, max_escalation_shifts_per_person, people)
    except rota.NoSatisfyingRotaError:
        return flask.render_template('error.html', message="There is no rota meeting the constraints!  Try a shorter rota, or allowing more shifts per person."), 500
    except rota.SolverError as e:
        return flask.render_template('error.html', summary="Encountered an internal solver error", message=f"The first invalid week is week {e.week}: {e.problem}.", debug=e.dump), 500

    rota_csv_string = printer.generate_rota_csv(num_weeks, people, model)
    return flask.Response(rota_csv_string, mimetype = 'text/plain')
