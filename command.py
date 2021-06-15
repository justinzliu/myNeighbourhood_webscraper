import pymongo

import compareSchool as cs
import db_msql as msql

DRIVER_PATH = "/usr/lib/chromium-browser/chromedriver"
CITY = "Burnaby"
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

#TODO: will likely need scrape dispatch for each website to scrape
def scrape_cmd(city):
	table = "schools"
	pkeys = ["city","name"]
	schools = cs.get_schools(city,DRIVER_PATH)
	msql.insert(table,pkeys,schools)

def msql_dispatch(*args):
	cases = {
		"ini": msql.ini,
		"reset": msql.reset
	}
	if cases.get(args[0]) == None:
		print("unknown command")
	else:
		cases[args[0]](*args[1:])

###Commands###
#scrape _1_ _2_:
#   _1_: website
#   _2_: specifics (city)
#   _3_: driver path
#db _1_ _2_:
#   _1_: database type
#   _2_: command (ini for db initialization)

#TODO: if possible, convert to command dispatch pattern
#https://stackoverflow.com/questions/5431732/patterns-event-dispatcher-without-else-if
def cmd_dispatch(cmd,args):
	live = 1
	cases = {
		"scrape": scrape_cmd,
		"db_msql": msql_dispatch
	}
	if cmd == "quit":
		live = 0
	elif cases.get(cmd) == None:
		print("unknown command")
	else:
		cases[cmd](*args)
	return live

if __name__ == "__main__":
	live = 1
	while live:
		cmd = input()
		cmd_split = cmd.split(sep=" ")
		live = cmd_dispatch(cmd_split[0], cmd_split[1:])