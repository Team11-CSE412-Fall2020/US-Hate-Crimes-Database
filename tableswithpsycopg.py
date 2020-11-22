import csv
import psycopg2

biasDict = dict()
offenseDict = dict()
agencyDict = dict()
locationDict = dict()
locationInd = 0
agencyInd = 0
biasInd = 0
offenseInd = 0

def tableCreate(conn):
    cur = conn.cursor()

    cur.execute('''CREATE TABLE locations (
    location_id SERIAL PRIMARY KEY,
    type_of TEXT,
    region TEXT,
    state_name TEXT,
    division TEXT,
    citysizerange TEXT);''')

    cur.execute('''CREATE TABLE agency (
    agency_id SERIAL PRIMARY KEY,
    agency_name TEXT,
    agency_type TEXT);''')

    cur.execute('''CREATE TABLE incident (
    incident_id SERIAL PRIMARY KEY,
    incident_year INT,
    incident_date DATE,
    number_of_offenses TEXT,
    reported_by INT,
    occurred_in INT,
    FOREIGN KEY (reported_by) REFERENCES agency (agency_id),
    FOREIGN KEY (occurred_in) REFERENCES locations (location_id));''')

    cur.execute('''CREATE TABLE based_in (
    location_id INT,
    agency_id INT,
    PRIMARY KEY (location_id, agency_id),
    FOREIGN KEY (location_id) REFERENCES locations (location_id),
    FOREIGN KEY (agency_id) REFERENCES agency (agency_id));''')

    cur.execute('''CREATE TABLE offense (
    offense_id SERIAL PRIMARY KEY,
    offensename TEXT);''')

    cur.execute('''CREATE TABLE types_of (
    incident_id INT,
    offense_id INT,
    PRIMARY KEY (incident_id, offense_id),
    FOREIGN KEY (incident_id) REFERENCES incident (incident_id),
    FOREIGN KEY (offense_id) REFERENCES offense (offense_id));''')

    cur.execute('''CREATE TABLE offender (
    offender_id SERIAL PRIMARY KEY,
    race TEXT,
    number_of_offenders INT,
    numberofbiases TEXT);''')

    cur.execute('''CREATE TABLE victim (
    victim_id SERIAL PRIMARY KEY,
    number_of_victims INT,
    victim_type TEXT);''')

    cur.execute('''CREATE TABLE bias (
    bias_id SERIAL PRIMARY KEY,
    bias_desc TEXT);''')

    cur.execute('''CREATE TABLE because_of (
    victim_id INT,
    bias_id INT,
    PRIMARY KEY (victim_id, bias_id),
    FOREIGN KEY (victim_id) REFERENCES victim (victim_id),
    FOREIGN KEY (bias_id) REFERENCES bias (bias_id));''')

    cur.execute('''CREATE TABLE motivated_by (
    offender_id INT,
    bias_id INT,
    PRIMARY KEY (offender_id, bias_id),
    FOREIGN KEY (offender_id) REFERENCES offender (offender_id),
    FOREIGN KEY (bias_id) REFERENCES bias (bias_id));''')

    cur.execute('''CREATE TABLE committed_against (
    incident_id INT,
    victim_id INT,
    PRIMARY KEY (incident_id, victim_id),
    FOREIGN KEY (incident_id) REFERENCES incident (incident_id),
    FOREIGN KEY (victim_id) REFERENCES victim (victim_id));''')

    cur.execute('''CREATE TABLE committed_by (
    incident_id INT,
    offender_id INT,
    PRIMARY KEY (incident_id, offender_id),
    FOREIGN KEY (incident_id) REFERENCES incident (incident_id),
    FOREIGN KEY (offender_id) REFERENCES offender (offender_id));''')

    cur.close()

    conn.commit()

with open("./hate_crime.csv", 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file)

    conn = psycopg2.connect(dbname="412db", user="postgres", password="password", port=8888)

    cur = conn.cursor()
    # tableCreate(conn)
    insertquery = "INSERT INTO {} ({}) VALUES ({});"

    for ind, row in enumerate(csv_reader):
        if ind % 10000 == 0:
            print("{} rows inserted".format(ind))
        locationKey = (row["REGION_NAME"].strip(), row["STATE_NAME"].strip(), row["DIVISION_NAME"].strip(), row["POPULATION_GROUP_DESC"].strip())
        if not locationKey in locationDict:
            locationDict[locationKey] = locationInd
            locationInd += 1
            locInsert = insertquery.format("locations", "location_id, region, state_name, division, citysizerange", "{}, $${}$$, $${}$$, $${}$$, $${}$$".format(locationDict[locationKey], row["REGION_NAME"], row["STATE_NAME"], row["DIVISION_NAME"], row["POPULATION_GROUP_DESC"]))
            # print(locInsert)
            cur.execute(locInsert)

        agencyKey = (row["PUB_AGENCY_NAME"].strip(), row["AGENCY_TYPE_NAME"].strip())
        if not agencyKey in agencyDict:
            agencyDict[agencyKey] = agencyInd
            agencyInd += 1
            agencyInsert = insertquery.format("agency", "agency_id, agency_name, agency_type", "{}, $${}$$, $${}$$".format(agencyDict[agencyKey], row["PUB_AGENCY_NAME"], row["AGENCY_TYPE_NAME"]))
            cur.execute(agencyInsert)
            cur.execute(insertquery.format("based_in", "agency_id, location_id", "{}, {}".format(agencyDict[agencyKey], locationDict[locationKey])))


        incInsert = insertquery.format("incident", "incident_id, incident_year, incident_date, number_of_offenses, reported_by, occurred_in", "{}, {}, $${}$$, $${}$$, {}, {}".format(ind, row["DATA_YEAR"], row["INCIDENT_DATE"], row["MULTIPLE_OFFENSE"], agencyDict[agencyKey], locationDict[locationKey]))
        cur.execute(incInsert)

        offense_desc = row["OFFENSE_NAME"]
        offenses = offense_desc.split(';')
        for b in offenses:
            b = b.strip()
            if not b in offenseDict:
                offenseDict[b] = offenseInd
                offenseInd += 1
                cur.execute(insertquery.format("offense", "offense_id, offensename", "{}, $${}$$".format(offenseDict[b], b)))
            cur.execute(insertquery.format("types_of", "incident_id, offense_id", "{}, {}".format(ind, offenseDict[b])))

        offInsert = insertquery.format("offender", "offender_id, race, number_of_offenders, numberofbiases", "{}, $${}$$, {}, $${}$$".format(ind, row["OFFENDER_RACE"], row["TOTAL_OFFENDER_COUNT"], row["MULTIPLE_BIAS"]))
        cur.execute(offInsert)

        if (row["TOTAL_INDIVIDUAL_VICTIMS"] is ""):
            vicInsert = insertquery.format("victim", "victim_id, number_of_victims, victim_type", "{}, {}, $${}$$".format(ind, 0, row["VICTIM_TYPES"]))
        else:
            vicInsert = insertquery.format("victim", "victim_id, number_of_victims, victim_type", "{}, {}, $${}$$".format(ind, row["TOTAL_INDIVIDUAL_VICTIMS"], row["VICTIM_TYPES"]))
        cur.execute(vicInsert)

        bias_desc = row["BIAS_DESC"]
        biases = bias_desc.split(';')
        for b in biases:
            b = b.strip()
            if not b in biasDict:
                biasDict[b] = biasInd
                biasInd += 1
                cur.execute(insertquery.format("bias", "bias_id, bias_desc", "{}, $${}$$".format(biasDict[b], b)))
            cur.execute(insertquery.format("because_of", "victim_id, bias_id", "{}, {}".format(ind, biasDict[b])))
            cur.execute(insertquery.format("motivated_by", "offender_id, bias_id", "{}, {}".format(ind, biasDict[b])))

        cur.execute(insertquery.format("committed_against", "incident_id, victim_id", "{}, {}".format(ind, ind)))
        cur.execute(insertquery.format("committed_by", "incident_id, offender_id", "{}, {}".format(ind, ind)))
        
    cur.close()

    conn.commit()

    conn.close()
