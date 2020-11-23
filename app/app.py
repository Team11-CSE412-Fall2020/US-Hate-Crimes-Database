
from flask import Flask, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy
from queries import runQuery
import os
import psycopg2


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
        
        Props['columns'], Props['allRows'] = runQuery(columns, conditions, Props['conn'])
        Props['rowCount'] = len(Props['allRows'])

        Props['rows'] = Props['allRows'][0:100]
        Props['pageNum'] = 0
        

        return render_template("index.html", Props = Props)


@app.route('/forward', methods=["GET", "POST"])
def forward():
    if request.method == "POST":

        #Avoid the -1 indexed page (empty)
        if Props['pageNum'] == -2:
            Props['pageNum'] += 2
        else:
            Props['pageNum'] += 1

        page = 100*Props['pageNum']
        Props['rows'] = Props['allRows'][(0+page):(100+page)]

        return render_template("index.html", Props = Props)


@app.route('/backward', methods=["GET", "POST"])
def backward():
    if request.method == "POST":

        #Avoid the -1 indexed page (empty)
        if Props['pageNum'] == 0:
            Props['pageNum'] += -2
        else:
            Props['pageNum'] += -1
        
        page = 100*Props['pageNum']
        Props['rows'] = Props['allRows'][(0+page):(100+page)]

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
    conn = psycopg2.connect(dbname="412db", user="postgres", password="barrow22")

    # Main data structure to pass around values between page reloads
    Props = {

        # SQL query content, tuple containing dictionaries representing the rows
        'allRows' : ((), ()),
        'rows' : ((), ()),
        'columns' : ("", ""),
        'conditions' : "",

        # len(rows), must be recalculated in .py file after a query
        'rowCount' : 0,
        'pageNum' : 0,

        'displayType' : "table",
        'conn' : conn,
    }

    
    # TODO: RUN SQL FIRST QUEREY HERE
    # Props['rows'] = SQLQUERY

    Props['rowCount'] = len(Props['rows'])

    app.run(debug=True)
    conn.close()