
from flask import Flask, render_template, url_for, request, Response
from flask_sqlalchemy import SQLAlchemy
from queries import runQuery
from queries import runQuery2
import os
import io
import random
import psycopg2
from itertools import groupby
import json

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = ''
# db = SQLAlchemy(app)

# def pass(database_name, user, password, port):


@app.route('/')
def index():
    return render_template('login.html', Props = Props)

@app.route('/home', methods=["GET", "POST"])
def home():
    if request.method == "POST":
        
        db_name = request.form['db-form']
        username = request.form['username-form']
        password = request.form['password-form']
        port = request.form['port-form']

        try:
            conn = psycopg2.connect(dbname=db_name, user=username, password=password, port=port)
            Props['loginFailed'] = False
        except:
            Props['loginFailed'] = True
            return render_template('login.html', Props=Props)

        Props['conn'] = conn
        Props['rowCount'] = len(Props['rows'])

        return render_template("index.html", Props=Props, Statistics = Statistics)


@app.route('/filter', methods=["GET", "POST"])
def filter():
    if request.method == "POST":
        
        Props['displayType'] = "table"
        columns = request.form['columns']
        conditions = request.form['conditions']
        Props['columns'], Props['allRows'] = runQuery(columns, conditions, Props['conn'])

        if Props['columns'] == () or Props['allRows'] == ():
            print("Invalid transaction")
            Props['displayType'] = 'error'
            Props['rowCount'] = 0
            return render_template("index.html", Props = Props) 


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


@app.route('/stats', methods=["GET", "POST"])
def stats():
    if request.method == "POST":
        Props['displayType'] = "stats"

        return render_template("index.html", Props = Props, Statistics = Statistics)

    return render_template("index.html", Props = Props, Statistics = Statistics)

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
    
    # Temp = {
    #     'allRows': ((), ()),
    #     'rows' : ((), ()),
    #     'columns' : ("", ""),
    #     'conn' : conn
    # }

    # tempColumn = 'offense.offensename, COUNT(*)'
    # tempCondition = 'GROUP BY offense.offensename'
    # Temp['columns'], Temp['allRows'] = runQuery2(tempColumn, tempCondition, Temp['conn'])
    # Temp['rows'] = Temp['allRows'][0:100]
    # with open('app/static/temp.json', 'a') as f:
    #     f.write('\n')
    #     f.write(json.dumps(Temp['rows']))

    # statsList = []
    # with open('app/static/temp.json', 'r') as f:
    #     print(type(json.load(f)))
    # Statistics = {
    #     'offenseNames' : statsList
    # }

    statsList = []
    with open('app/static/statistics.json', 'r') as f:
        listList = f.readlines()
        for tempList in listList:
            newItem = json.loads(tempList)
            statsList.append(newItem)

    Statistics = {
        'offenseNames' : statsList[0],
        'offenderRace' : statsList[1],
        'victimCount' : statsList[2],
        'region' : statsList[3],
        'stateName' : statsList[4],
        'year' : statsList[5],
        'popDesc' : statsList[6],
        'agencyType' : statsList[7]
    }

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
        'conn' : None,
        'loginFailed' : False,
    }
    

    # TODO: RUN SQL FIRST QUEREY HERE
    # Props['rows'] = SQLQUERY
    app.run(debug=True)
    Props['conn'].close()
    # conn.close()