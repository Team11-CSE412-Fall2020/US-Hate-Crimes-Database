import psycopg2;

basicquery = '''SELECT {} FROM incident, locations, agency, based_in,
offense, types_of, offender, committed_by, victim, committed_against,
bias, because_of, motivated_by
WHERE incident.occurred_in = locations.location_id AND 
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
offender.offender_id = motivated_by.offender_id AND ({})
;'''.format("agency.agency_name", "locations.state_name = \'Arizona\' AND incident.incident_id < 6000")

if __name__ == "__main__":
    conn = psycopg2.connect(dbname="412db", user="postgres", password="password", port=8888)
    
    cur = conn.cursor()

    cur.execute(basicquery)

    # print(cur.fetchone())

    # print(len(cur.fetchall()))
    print(cur.fetchall())

    cur.close()

    conn.close()
