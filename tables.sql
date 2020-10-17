CREATE TABLE locations (
    location_id SERIAL PRIMARY KEY,
    region TEXT,
    state_name TEXT,
    division TEXT,
    citysizerange TEXT
);

CREATE TABLE agency (
    agency_id SERIAL PRIMARY KEY,
    agency_name TEXT,
    agency_type TEXT
);

CREATE TABLE incident (
    incident_id SERIAL PRIMARY KEY,
    incident_year INT,
    incident_date DATE,
    number_of_offenses TEXT,
    reported_by INT,
    occurred_in INT,
    FOREIGN KEY (occurred_in) REFERENCES locations (location_id),
    FOREIGN KEY (reported_by) REFERENCES agency (agency_id)
);


CREATE TABLE based_in (
    location_id INT,
    agency_id INT,
    PRIMARY KEY (location_id, agency_id),
    FOREIGN KEY (location_id) REFERENCES locations (location_id),
    FOREIGN KEY (agency_id) REFERENCES agency (agency_id)
);

CREATE TABLE offense (
    offense_id SERIAL PRIMARY KEY,
    offensename TEXT
);

CREATE TABLE types_of (
    incident_id INT,
    offense_id INT,
    PRIMARY KEY (incident_id, offense_id),
    FOREIGN KEY (incident_id) REFERENCES incident (incident_id),
    FOREIGN KEY (offense_id) REFERENCES offense (offense_id)
);

CREATE TABLE offender (
    offender_id SERIAL PRIMARY KEY,
    race TEXT,
    number_of_offenders INT,
    numberofbiases TEXT
);

CREATE TABLE victim (
    victim_id SERIAL PRIMARY KEY,
    number_of_victims INT,
    victim_type TEXT
);

CREATE TABLE bias (
    bias_id SERIAL PRIMARY KEY,
    bias_desc TEXT
);

CREATE TABLE because_of (
    victim_id INT,
    bias_id INT,
    PRIMARY KEY (victim_id, bias_id),
    FOREIGN KEY (victim_id) REFERENCES victim (victim_id),
    FOREIGN KEY (bias_id) REFERENCES bias (bias_id)
);

CREATE TABLE motivated_by (
    offender_id INT,
    bias_id INT,
    PRIMARY KEY (offender_id, bias_id),
    FOREIGN KEY (offender_id) REFERENCES offender (offender_id),
    FOREIGN KEY (bias_id) REFERENCES bias (bias_id)
);

CREATE TABLE committed_against (
    incident_id INT,
    victim_id INT,
    PRIMARY KEY (incident_id, victim_id),
    FOREIGN KEY (incident_id) REFERENCES incident (incident_id),
    FOREIGN KEY (victim_id) REFERENCES victim (victim_id)
);

CREATE TABLE committed_by (
    incident_id INT,
    offender_id INT,
    PRIMARY KEY (incident_id, offender_id),
    FOREIGN KEY (incident_id) REFERENCES incident (incident_id),
    FOREIGN KEY (offender_id) REFERENCES offender (offender_id)
);
