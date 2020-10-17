import csv

biasDict = dict()
offenseDict = dict()
agencyDict = dict()
locationDict = dict()
locationInd = 0
agencyInd = 0
biasInd = 0
offenseInd = 0

with open("./hate_crime.csv", 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    with open('./split_csvs/incident.csv', 'w') as incCSV, \
        open('./split_csvs/locations.csv', 'w') as locCSV, \
        open('./split_csvs/agency.csv', 'w') as agencyCSV, \
        open('./split_csvs/based_in.csv', 'w') as basedCSV, \
        open('./split_csvs/offense.csv', 'w') as offenseCSV, \
        open('./split_csvs/types_of.csv', 'w') as typesCSV, \
        open('./split_csvs/offender.csv', 'w') as offenderCSV, \
        open('./split_csvs/victim.csv', 'w') as victCSV, \
        open('./split_csvs/bias.csv', 'w') as biasCSV, \
        open('./split_csvs/because_of.csv', 'w') as bcofCSV, \
        open('./split_csvs/motivated_by.csv', 'w') as motivatedCSV, \
        open('./split_csvs/committed_against.csv', 'w') as comAgCSV, \
        open('./split_csvs/committed_by.csv', 'w') as comByCSV:
        
        incWriter = csv.DictWriter(incCSV, fieldnames = ['incident_id', 'incident_year', 'incident_date', 'number_of_offenses', 'reported_by', 'occurred_in'], lineterminator = '\n')
        incWriter.writerow(dict((fn,fn) for fn in incWriter.fieldnames))
        locWriter = csv.DictWriter(locCSV, fieldnames = ['location_id', 'region', 'state_name', 'division', 'citysizerange'], lineterminator = '\n')
        locWriter.writerow(dict((fn,fn) for fn in locWriter.fieldnames))
        agencyWriter = csv.DictWriter(agencyCSV, fieldnames = ["agency_id", "agency_name", "agency_type"], lineterminator = '\n')
        agencyWriter.writerow(dict((fn,fn) for fn in agencyWriter.fieldnames))
        basedWriter = csv.DictWriter(basedCSV, fieldnames = ["location_id", "agency_id"], lineterminator = '\n')
        basedWriter.writerow(dict((fn,fn) for fn in basedWriter.fieldnames))
        offenseWriter = csv.DictWriter(offenseCSV, fieldnames=["offense_id", "offensename"], lineterminator = '\n')
        offenseWriter.writerow(dict((fn,fn) for fn in offenseWriter.fieldnames))
        typesWriter = csv.DictWriter(typesCSV, fieldnames = ['incident_id', 'offense_id'], lineterminator = '\n')
        typesWriter.writerow(dict((fn,fn) for fn in typesWriter.fieldnames))
        offenderWriter = csv.DictWriter(offenderCSV, fieldnames = ['offender_id', 'race', 'number_of_offenders', 'numberofbiases'], lineterminator = '\n')
        offenderWriter.writerow(dict((fn,fn) for fn in offenderWriter.fieldnames))
        victWriter = csv.DictWriter(victCSV, fieldnames = ["victim_id", "number_of_victims", "victim_type"], lineterminator = '\n')
        victWriter.writerow(dict((fn,fn) for fn in victWriter.fieldnames))
        biasWriter = csv.DictWriter(biasCSV, fieldnames=["bias_id","bias_desc"], lineterminator = '\n')
        biasWriter.writerow(dict((fn,fn) for fn in biasWriter.fieldnames))
        bcofWriter = csv.DictWriter(bcofCSV, fieldnames=["victim_id", "bias_id"], lineterminator = '\n')
        bcofWriter.writerow(dict((fn,fn) for fn in bcofWriter.fieldnames))
        motivatedWriter = csv.DictWriter(motivatedCSV, fieldnames=["offender_id", "bias_id"], lineterminator = '\n')
        motivatedWriter.writerow(dict((fn,fn) for fn in motivatedWriter.fieldnames))
        comAgWriter = csv.DictWriter(comAgCSV, fieldnames=["incident_id", "victim_id"], lineterminator = '\n')
        comAgWriter.writerow(dict((fn,fn) for fn in comAgWriter.fieldnames))
        comByWriter = csv.DictWriter(comByCSV, fieldnames=["incident_id", "offender_id"], lineterminator = '\n')
        comByWriter.writerow(dict((fn,fn) for fn in comByWriter.fieldnames))

        for ind, row in enumerate(csv_reader):
            locationKey = (row["REGION_NAME"].strip(), row["STATE_NAME"].strip(), row["DIVISION_NAME"].strip(), row["POPULATION_GROUP_DESC"].strip())
            if not locationKey in locationDict:
                locationDict[locationKey] = locationInd
                locationInd += 1
                loc = {"location_id": locationDict[locationKey], "region": row["REGION_NAME"], "state_name": row["STATE_NAME"], "division": row["DIVISION_NAME"], "citysizerange": row["POPULATION_GROUP_DESC"]}
                locWriter.writerow(loc)

            agencyKey = (row["PUB_AGENCY_NAME"].strip(), row["AGENCY_TYPE_NAME"].strip())
            if not agencyKey in agencyDict:
                agencyDict[agencyKey] = agencyInd
                agencyInd += 1
                agency = {"agency_id": agencyDict[agencyKey], "agency_name": row["PUB_AGENCY_NAME"], "agency_type": row["AGENCY_TYPE_NAME"]}
                agencyWriter.writerow(agency)
                basedWriter.writerow({"agency_id": agencyDict[agencyKey], "location_id": locationDict[locationKey]})

            offense_desc = row["OFFENSE_NAME"]
            offenses = offense_desc.split(';')
            for b in offenses:
                b = b.strip()
                if not b in offenseDict:
                    offenseDict[b] = offenseInd
                    offenseInd += 1
                    offenseWriter.writerow({"offense_id": offenseDict[b], "offensename": b})
                typesWriter.writerow({"incident_id": ind, "offense_id": offenseDict[b]})

            incident = {"incident_id": ind, "incident_year": row["DATA_YEAR"], "incident_date": row["INCIDENT_DATE"], "number_of_offenses": row["MULTIPLE_OFFENSE"], "reported_by": agencyDict[agencyKey], "occurred_in": locationDict[locationKey]}
            incWriter.writerow(incident)

            offender = {"offender_id": ind, "race": row["OFFENDER_RACE"], "number_of_offenders": row["TOTAL_OFFENDER_COUNT"], "numberofbiases": row["MULTIPLE_BIAS"]}
            offenderWriter.writerow(offender)

            victim = {"victim_id": ind, "number_of_victims": row["TOTAL_INDIVIDUAL_VICTIMS"], "victim_type": row["VICTIM_TYPES"]}
            victWriter.writerow(victim)

            bias_desc = row["BIAS_DESC"]
            biases = bias_desc.split(';')
            for b in biases:
                b = b.strip()
                if not b in biasDict:
                    biasDict[b] = biasInd
                    biasInd += 1
                    biasWriter.writerow({"bias_id": biasDict[b], "bias_desc": b})
                bcofWriter.writerow({"victim_id": ind, "bias_id": biasDict[b]})
                motivatedWriter.writerow({"offender_id": ind, "bias_id": biasDict[b]})

            comAgWriter.writerow({"incident_id": ind, "victim_id": ind})
            comByWriter.writerow({"incident_id": ind, "offender_id": ind})