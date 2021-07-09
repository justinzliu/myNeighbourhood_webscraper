import mysql.connector
from datetime import date as date

DATABASE_NAME = "myNeighbourhood"
TABLES = {}
TABLES["schools"] = (
    "CREATE TABLE schools ("
    "  `city` VARCHAR(255) NOT NULL,"
    "  `name` VARCHAR(255) NOT NULL,"
    "  `score` VARCHAR(255),"
    "  `rank` VARCHAR(255),"
    "  `retrieved` DATE,"
    "  PRIMARY KEY (`city`, `name`)"
    ")")
TABLES["crimes"] = (
    "CREATE TABLE crimes ("
    "  `location` VARCHAR(255) NOT NULL,"
    "  `violations` VARCHAR(255) NOT NULL,"
    "  `incidents` VARCHAR(255),"
    "  `rate` VARCHAR(255),"
    "  `change` VARCHAR(255),"
    "  `year` VARCHAR(255),"
    "  `retrieved` DATE,"
    "  PRIMARY KEY (`location`, `violations`)"
    ")")

###############
### Utility ###
###############

#elem_brackets and enclosure must be a pair of strings that will enclose the element and the list of elements respectively
def enclose(elem, elem_brackets="  ", enclosure="  "):
	separator = elem_brackets[1] + ", " + elem_brackets[0]
	enclosed = enclosure[0] + elem_brackets[0] + separator.join(elem) + elem_brackets[1] + enclosure[1]
	return enclosed

######################
### mySQL Commands ###
######################

def ini(host="localhost", user="root", password=""):
	conn = mysql.connector.connect(
	  host=host,
	  user=user,
	  password=password
	)
	cursor = conn.cursor()
	cursor.execute("CREATE DATABASE " + DATABASE_NAME)
	try:
		cursor.execute("use " + DATABASE_NAME)
		cursor.execute(TABLES["schools"])
		cursor.execute(TABLES["crimes"])
	except mysql.connector.Error as err:
		print("ERROR db_msql.ini(): " + format(err))
	finally:
		cursor.close()
		conn.close()

#SQL command INSERT INTO _ VALUES _ ON DUPLICATE KEY UPDATE
def insert(table, pkeys, entries):
	conn = mysql.connector.connect(
	  host="localhost",
	  user="root",
	  password="",
	  database=DATABASE_NAME
	)
	cursor = conn.cursor()
	try:
		cols = entries[0].__dict__.keys()
		cols_nokey = [col for col in cols if col not in pkeys]
		cmd_prefix_values = "VALUES "
		cmd_prefix_update = "ON DUPLICATE KEY UPDATE "
		for entry in entries:
			cmd_template = (
				"INSERT INTO " + table + " " + enclose(cols,"``","()") +
				" VALUES " + enclose(cols,["%(",")s"],"()") + 
				" ON DUPLICATE KEY UPDATE " + ", ".join([("`" + col + "`" + "='" + getattr(entry, col) + "'") for col in cols_nokey])
				)
			cursor.execute(cmd_template, entry.__dict__)
			conn.commit()
	except mysql.connector.Error as err:
		print("ERROR db_msql.insert(): " + format(err))
	finally:
		cursor.close()
		conn.close()

#TESTING: remove when production-ready
def reset():
	conn = mysql.connector.connect(
	  host="localhost",
	  user="root",
	  password="",
	)
	cursor = conn.cursor()
	try:
		cursor.execute("DROP DATABASE " + DATABASE_NAME)
	except mysql.connector.Error as err:
		print("ERROR db_msql.reset(): " + format(err))
	finally:
		cursor.close()
		conn.close()