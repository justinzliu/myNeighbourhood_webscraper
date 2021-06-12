import mysql.connector

DATABASE_NAME = "myNeighbourhood"
TABLES = {}
TABLES["schools"] = (
    "CREATE TABLE schools ("
    "  `city` VARCHAR(255) NOT NULL,"
    "  `name` VARCHAR(255) NOT NULL,"
    "  `score` VARCHAR(255),"
    "  `rank` VARCHAR(255),"
    "  PRIMARY KEY (`city`, `name`)"
    ")")

###############
### Utility ###
###############

#elem_brackets and enclosure must be a pair of strings that will enclose the element and the list of elements respectively
def enclose(elem, elem_brackets="  ", enclosure="  "):
	separator = elem_brackets[0] + ", " + elem_brackets[1]
	enclosed = enclosure[0] + elem_brackets[0] + separator.join(elem) + elem_brackets[1] + enclosure[1]
	return enclosed

######################
### mySQL commands ###
######################

def ini():
	#TODO: look into secure solution for connection without code exposing login information
	conn = mysql.connector.connect(
	  host="localhost",
	  user="root",
	  password=""
	)
	cursor = conn.cursor()
	#cursor.execute("CREATE DATABASE " + DATABASE_NAME)
	try:
		cursor.execute("use " + DATABASE_NAME)
		cursor.execute(TABLES["schools"])
	except mysql.connector.Error as err:
		print("ERROR: " + format(err))
	finally:
		conn.close()

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
		cmd_insertinto = "INSERT INTO " + table + " " + enclose(cols,"``","()")
		#print(cmd_insertinto)
		cmd_prefix_values = "VALUES "
		cmd_prefix_update = "ON DUPLICATE KEY UPDATE "
		for entry in entries:
			cmd_val_format = []
			for col in cols:
				cmd_val_format.append(getattr(entry, col))
			cmd_entry_values = cmd_prefix_values + enclose(cmd_val_format,"''","()")
			cmd_colval_format = []
			for col in cols_nokey:
				cmd_colval_format.append("`" + col + "`" + "='" + getattr(entry, col) + "'")
			cmd_entry_update = cmd_prefix_update + ", ".join(cmd_colval_format)
			#print(cmd_entry_values)
			#print(cmd_entry_update)
		cmd = " ".join([cmd_insertinto, cmd_entry_values, cmd_entry_update])
		#print(cmd)
		cursor.execute(cmd)
		conn.commit()
	except Exception as e:
		print('ERROR db_msql.insert(): ', e)
	finally:
		cursor.close()
		conn.close()

class School:
	#pass -1 for score and "n/a" for rank when not applicable 
	def __init__(self, city, name, score, rank):
		self.city = city
		self.name = name
		self.score = score
		self.rank = rank
	def __str__(self):
		return (" ".join([self.name,self.score,self.rank]))

#DEBUG: TESTING
schl = School("Burnaby","daSchool","100","2")
TESTIN_1 = "schools"
TESTIN_2 = ["city","name"]
TESTIN_3 = [schl]
insert(TESTIN_1, TESTIN_2, TESTIN_3)
#ini()


#nolist = ["name", "rank"]
#keys = test.__dict__.keys()
#keys_filtered = [i for i in keys if i not in nolist]
#print(", ".join(keys_filtered))
#print(", ".join(keys))
#for key in keys:
#	val = getattr(test,key)
#	print(val)