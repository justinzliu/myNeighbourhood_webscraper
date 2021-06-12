import pymongo
import mysql.connector

import compareSchool as cs
import db_msql as msql

DRIVER_PATH = "/usr/lib/chromium-browser/chromedriver"
CITY = "Burnaby"
DATABASE_NAME = "myNeighbourhood"
DATABASE_PORT = "27017"
MSQL_LOGIN = {
	"host": "localhost",
	"user": "root",
	"password": "",
}

#TODO: mongoDB functions
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

###Commands###
#scrape _1_ _2_:
#   _1_: website
#   _2_: specifics (city)
#db _1_ _2_:
#   _1_: database type
#   _2_: command (ini for db initialization)

#TODO: if possible, convert to command dispatch pattern
#https://stackoverflow.com/questions/5431732/patterns-event-dispatcher-without-else-if
def process_cmd(cmd,args):
	live = 1
	cases = {
		"scrape": print("call cs.get_schools()"), #cs.get_schools(CITY, DRIVER_PATH),
		"db": print("call database()"), #database()
	}
	if cmd == "quit":
		live = 0
	else:
		if cases.get(cmd) == None:
			print("unknown command")
	return live

if __name__ == "__main__":
	live = 1
	while live:
		cmd = input()
		cmd_split = cmd.split(sep=" ")
		live = process_cmd(cmd_split[0], cmd_split[1:])