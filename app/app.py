
from flask import Flask, render_template, url_for, request, Response
from flask_sqlalchemy import SQLAlchemy
from queries import runQuery
import os
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import random
import psycopg2
from itertools import groupby


app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = ''
# db = SQLAlchemy(app)

# def pass(database_name, user, password, port):


@app.route('/')
def index():
    return render_template('index.html', Props = Props)


@app.route('/filter', methods=["GET", "POST"])
def filter():
    if request.method == "POST":

        columns = request.form['columns']
        conditions = request.form['conditions']
        
        Props['rows'] = runQuery(columns, conditions, Props['conn'])[1:]
        Props['rowCount'] = len(Props['rows'])
        
        #TODO: RUN FILTER QUERY HERE ON PROPS
        #
        #Props['rows'] = newTuple

        return render_template("index.html", Props = Props)


@app.route('/table', methods=["GET", "POST"])
def table():
    if request.method == "POST":
        Props['displayType'] = "table"

        return render_template("index.html", Props = Props)

    return render_template("index.html", Props = Props)


@app.route('/graph', methods=["GET", "POST"])
def graph():
    if request.method == "POST":
        Props['displayType'] = "graph"

        return render_template("index.html", Props = Props)

    return render_template("index.html", Props = Props)

@app.route('/state_plot.png')
def plot_png():
    cur = conn.cursor()
    cur.execute('''SELECT locations.state_name FROM incident, locations, agency, based_in,
    offense, types_of, offender, committed_by, victim, committed_against,
    bias, because_of, motivated_by WHERE incident.occurred_in = locations.location_id AND 
    incident.reported_by = agency.agency_id AND
    locations.location_id = based_in.location_id AND
    agency.agency_id = based_in.agency_id AND
    incident.incident_id = types_of.incident_id AND
    offense.offense_id = types_of.offense_id AND
    committed_by.incident_id = incident.incident_id AND
    committed_by.offender_id = offender.offender_id AND
    committed_against.incident_id = incident.incident_id AND
    committed_against.victim_id = victim.victim_id AND
    bias.bias_id = because_of.bias_id AND
    victim.victim_id = because_of.victim_id AND
    bias.bias_id = motivated_by.bias_id AND
    offender.offender_id = motivated_by.offender_id;''')
    stateList = cur.fetchall()
    stateListFlat = []
    for i in stateList:
        stateListFlat.append(i[0])
    stateListFlat.sort()
    frequency = [len(list(group)) for key, group in groupby(stateListFlat)]
    stateListFlat = list(dict.fromkeys(stateListFlat))
    fig = Figure()
    fig.set_size_inches(11, 8)
    axis = fig.add_subplot(1, 1, 1)
    axis.bar(stateListFlat, frequency, color=(0.8, 0.0, 0.0, 0.6))
    axis.set_title('Number of Incidents per State')
    axis.set_ylabel('Frequency')
    plt.setp(axis.xaxis.get_majorticklabels(), rotation=90)
    fig.tight_layout()
    axis.figure.tight_layout()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype="image/png")

@app.route('/plot2.png')
def plot_png2():
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    xs = ["swag", "ok"]
    ys = [4, 6]
    axis.bar(xs, ys)
    axis.set_title('graph 2')
    axis.set_ylabel('numbers')
    axis.set_xlabel('time')
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

# Weird hack to get hot reloading working with browser-caching, can mostly ignore
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                 endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


if __name__ == "__main__":
    conn = psycopg2.connect(dbname="412project", user="postgres", password="password", port=5432)

    # Main data structure to pass around values between page reloads
    Props = {

        # SQL query content, tuple containing dictionaries representing the rows
        'rows' : ((), (),) ,
        'columns' : "",
        'conditions' : "",

        # len(rows), must be recalculated in .py file after a query
        'rowCount' : 0,

        'displayType' : "table",
        'conn' : conn,
    }

    
    # TODO: RUN SQL FIRST QUEREY HERE
    # Props['rows'] = SQLQUERY

    Props['rowCount'] = len(Props['rows'])

    app.run(debug=True)