import modules.webscraper.compareSchool as cs
import modules.db.msql as msql
import modules.webscraper.statsCanada as sc

DRIVER_PATH = "/usr/lib/chromium-browser/chromedriver"
CITY = "Burnaby"
LOCATION1 = "Canada"
LOCATION2 = ["British Columbia", "Burnaby", "Vancouver", "Surrey", "New Westminster", "Richmond"]
scCrime_PATH = "resources/crime_statistics/"
scCrime_FILE1 = "statscan_crime_canada.csv"
scCrime_FILE2 = "statscan_crime_bc.csv"
DATABASE_NAME = "myNeighbourhood"
DATABASE_PORT = "27017"

#TODO: REMOVE when production-ready
#TODO: run all scraping commands together for convenience
def scrape_cmd():
	cs_table = "schools"
	cs_pkeys = ["city","name"]
	#cs_schools = cs.get_schools(DRIVER_PATH, COUNTRY, LOCATION, SCHOOLTYPE)
	msql.insert(cs_table,cs_pkeys,cs_schools)
	scCrime_table = "crimes"
	scCrime_pkeys = ["location","violations"]
	scCrime_crimes = sc.get_reports(scCrime_PATH + scCrime_FILE1, LOCATION1)
	msql.insert(scCrime_table,scCrime_pkeys,scCrime_crimes)
	for location in LOCATION2:
		scCrime_crimes = sc.get_reports(scCrime_PATH + scCrime_FILE2, location)
		msql.insert(scCrime_table,scCrime_pkeys,scCrime_crimes)

def scrape(path, country, location):
	pass

def scrape_dispatch(*args):
	cases = {
		"compareschool": cs.get_schools,
		"statscanada": sc.get_reports
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