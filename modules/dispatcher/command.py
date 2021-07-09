import pymongo

import modules.webscraper.compareSchool as cs
import modules.db.msql as msql
import modules.webscraper.statsCanada_crime as scCrime

DRIVER_PATH = "/usr/lib/chromium-browser/chromedriver"
CITY = "Burnaby"
LOCATION1 = "Canada"
LOCATION2 = ["British Columbia", "Burnaby", "Vancouver", "Surrey", "New Westminster", "Richmond"]
scCrime_PATH = "resources/crime_statistics/"
scCrime_FILE1 = "statscan_crime_canada.csv"
scCrime_FILE2 = "statscan_crime_bc.csv"
DATABASE_NAME = "myNeighbourhood"
DATABASE_PORT = "27017"

#TODO: mongoDB functions, used for Realtor features
def pymongo_database():
	client = pymongo.MongoClient("mongodb://localhost:"+DATABASE_PORT+"/")
	db = client[DATABASE_NAME]

	#DEBUG: confirm db exists
	dblist = client.list_database_names()
	if DATABASE_NAME in dblist:
		print(DATABASE_NAME + " exists")

	#DEBUG: delete db
	client.drop_database(DATABASE_NAME)
	dblist = client.list_database_names()
	if DATABASE_NAME not in dblist:
		print(DATABASE_NAME + " successfully deleted")

	client.close()

#TODO: REMOVE when production-ready
#TODO: run all scraping commands together for convenience
def scrape_cmd():
	cs_table = "schools"
	cs_pkeys = ["city","name"]
	cs_schools = cs.get_schools(DRIVER_PATH,CITY)
	msql.insert(cs_table,cs_pkeys,cs_schools)
	scCrime_table = "crimes"
	scCrime_pkeys = ["location","violations"]
	scCrime_crimes = scCrime.get_reports(scCrime_PATH + scCrime_FILE1, LOCATION1)
	msql.insert(scCrime_table,scCrime_pkeys,scCrime_crimes)
	for location in LOCATION2:
		scCrime_crimes = scCrime.get_reports(scCrime_PATH + scCrime_FILE2, location)
		msql.insert(scCrime_table,scCrime_pkeys,scCrime_crimes)

def scrape_dispatch(*args):
	cases = {
		"compareschool": cs.get_schools,
		"statscanada": scCrime.get_reports
	}
	if cases.get(args[0]) == None:
		print("unknown command")
	else:
		cases[args[0]](*args[1:])

def msql_dispatch(*args):
	cases = {
		"ini": msql.ini,
		"reset": msql.reset
	}
	if cases.get(args[0]) == None:
		print("unknown command")
	else:
		cases[args[0]](*args[1:])

################
### Commands ###
################

#scrape _1_ _2_ _3_:
#   _1_: website
#   _2_: driver path
#   _3_: specifics (location)
#db _1_ _2_:
#   _1_: database type
#   _2_: command (ini for db initialization)

def cmd_dispatch(cmd,args):
	live = 1
	cases = {
		"scrape": scrape_cmd,
		"db_msql": msql_dispatch
	}
	try:
		if cmd == "quit":
			live = 0
		elif cases.get(cmd) == None:
			print("unknown command")
		else:
			cases[cmd](*args)
	except Exception as e:
		print('error cmd_dispatch:', e)
	finally:
		return live