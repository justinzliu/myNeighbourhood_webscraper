import csv
import re
from datetime import date as date

import mysql.connector

import modules.webscraper.scraper_utils as scrape

TEST_CONFIG = {
  'user': 'test',
  'password': 'Test123!',
  'host': 'localhost'
}
DATABASE_NAME = "myNeighbourhood"
TABLES = {}
PRIMARY_KEYS = {}
#Table Schemas
TABLES["locations"] = (
	"CREATE TABLE locations ("
	"  `loc_id` INT NOT NULL AUTO_INCREMENT UNIQUE,"
	"  `country` VARCHAR(100) NOT NULL,"
	"  `province` VARCHAR(100) NOT NULL,"
	"  `city` VARCHAR(100) NOT NULL,"
	"  PRIMARY KEY (`country`, `province`, `city`)"
	") ENGINE=InnoDB")
TABLES["sources"] = (
    "CREATE TABLE sources ("
	"  `loc_id` int NOT NULL,"
    "  `type` VARCHAR(50) NOT NULL,"
    "  `source` VARCHAR(100),"
    "  `method` VARCHAR(50),"
    "  `arguments` VARCHAR(255),"
    "  PRIMARY KEY (`loc_id`, `type`),"
	"  CONSTRAINT `sources_fk_1` FOREIGN KEY (`loc_id`) "
	"     REFERENCES `locations` (`loc_id`) ON DELETE CASCADE"
    ") ENGINE=InnoDB")
TABLES["schools"] = (
    "CREATE TABLE schools ("
	"  `loc_id` INT NOT NULL,"
    "  `name` VARCHAR(100) NOT NULL,"
	"  `type` VARCHAR(20) NOT NULL,"
    "  `score` VARCHAR(20),"
    "  `rank` VARCHAR(20),"
	"  `address` VARCHAR(255),"
	"  `coordinate` VARCHAR(50),"
    "  `retrieved` DATE,"
    "  PRIMARY KEY (`loc_id`, `name`, `type`),"
	"  CONSTRAINT `schools_fk_1` FOREIGN KEY (`loc_id`) "
	"     REFERENCES `locations` (`loc_id`) ON DELETE CASCADE"
    ") ENGINE=InnoDB")
TABLES["crimes"] = (
    "CREATE TABLE crimes ("
	"  `loc_id` int NOT NULL,"
    "  `violations` VARCHAR(100) NOT NULL,"
    "  `incidents` INT,"
    "  `rate` FLOAT,"
    "  `change` FLOAT,"
    "  `year` VARCHAR(10),"
    "  `retrieved` DATE,"
    "  PRIMARY KEY (`loc_id`, `violations`),"
	"  CONSTRAINT `crimes_fk_1` FOREIGN KEY (`loc_id`) "
	"     REFERENCES `locations` (`loc_id`) ON DELETE CASCADE"
    ") ENGINE=InnoDB")
TABLES["census"] = (
    "CREATE TABLE census ("
	"  `loc_id` int NOT NULL,"
    "  `population` VARCHAR(50) NOT NULL,"
    "  `ageGroups` VARCHAR(255),"
    "  `demographics` VARCHAR(510),"
    "  `avgAge` VARCHAR(50),"
    "  `avgIncome` VARCHAR(50),"
    "  `avgHouseIncome` VARCHAR(50),"
    "  `year` VARCHAR(10),"
    "  `retrieved` DATE,"
    "  PRIMARY KEY (`loc_id`),"
	"  CONSTRAINT `census_fk_1` FOREIGN KEY (`loc_id`) "
	"     REFERENCES `locations` (`loc_id`) ON DELETE CASCADE"
    ") ENGINE=InnoDB")
PRIMARY_KEYS["locations"] = ["country", "province", "city"]
PRIMARY_KEYS["sources"] = ["loc_id", "type"]
PRIMARY_KEYS["schools"] = ["loc_id", "name", "type"]
PRIMARY_KEYS["crimes"] = ["loc_id", "violations"]
PRIMARY_KEYS["census"] = ["loc_id"]

INI_PATH = "resources/conf/"
LOCATIONS_INI_FILE = "locations.csv"
SOURCES_INI_FILE = "sources.csv"

###############
### Utility ###
###############

#elem_brackets and enclosure must be a pair of strings that will enclose the element and the list of elements respectively
def enclose(list, elem_brackets="  ", enclosure="  "):
	separator = elem_brackets[1] + ", " + elem_brackets[0]
	enclosed = enclosure[0] + elem_brackets[0] + separator.join(list) + elem_brackets[1] + enclosure[1]
	return enclosed

#conjoin joins each element in each list of strings with seperator and returns a list of strings
def conjoin(list1, list2, seperator):
	joined = []
	for el1, el2 in zip(list1, list2):
		elem = el1 + seperator + '"' + el2 + '"'
		joined.append(elem)
	return joined

#creates database with desired tables
def ini_database(db_name, db_tables, db_config):
	conn = mysql.connector.connect(**db_config)
	cursor = conn.cursor()
	try:
		cursor.execute("CREATE DATABASE " + db_name)
		cursor.execute("use " + db_name)
		for key in db_tables:
			cursor.execute(db_tables[key])
	except mysql.connector.Error as err:
		print("ERROR msql.ini_database(): {}".format(err))
	finally:
		cursor.close()
		conn.close()

#update table from configuration file
def update_table_from_file(file, table, class_init, db_config):
	target_file = INI_PATH + file
	targets = []
	with open(target_file, "r", newline='', encoding='utf-8-sig') as file:
		reader = csv.DictReader(file, delimiter=',')
		for row in reader:
			target = class_init(row)
			targets.append(target)
	insert(table, targets, db_config)

#update sources table from configuration file (cannot use update_table_from_file due to conditions)
def update_sources(locations, db_config):
	sources_file = INI_PATH + SOURCES_INI_FILE
	sources = []
	with open(sources_file, "r", newline='', encoding='utf-8-sig') as file:
		reader = csv.DictReader(file, delimiter=',')
		for row in reader:
			target_loc = scrape.Location.init_dict(row)
			for location in locations: #TODO: this can be optimized with sorted() then binary search
				if location == target_loc:
					source = scrape.Source.init_dict(location.loc_id, row)
					sources.append(source)
	#print(sources)
	insert("sources", sources, db_config)

#class_init is a class init function
def select_format(table:str, class_init, conditions:dict={}, db_config:dict=TEST_CONFIG, db_name:str=DATABASE_NAME) -> list:
	targets = []
	tars = select(table, get_tblColumns(TABLES[table]), conditions, db_config, db_name)
	for tar in tars:
		target = class_init(*tar)
		targets.append(target)
	return targets

#get all primary keys from table description
def get_tblPkeys(table):
	pattern = re.compile("PRIMARY KEY (.*)")
	key_str = pattern.search(table).group()
	key_str = key_str[key_str.find("`")+1:key_str.find("`)")]
	keys = key_str.split("`, `")
	return keys

#get all columns from table description
def get_tblColumns(table):
	pattern = re.compile("  `[a-zA-Z_]*`")
	cols = pattern.findall(table)
	index = 0
	for col in cols:
		cols[index] = col.strip(" `")
		index += 1
	return cols

######################
### mySQL Commands ###
######################

def ini(db_config=TEST_CONFIG):
	try:
		ini_database(DATABASE_NAME, TABLES, db_config)
		#initialize database with supported locations
		update_table_from_file(LOCATIONS_INI_FILE, "locations", scrape.Location.init_dict, db_config)
		#retrieve locations from database for primary key loc_id
		locations = select_format("locations", scrape.Location, {}, TEST_CONFIG, DATABASE_NAME)
		#initialize database with location sources
		update_sources(locations, db_config)
	except mysql.connector.Error as err:
		print("ERROR db_msql.ini(): {}".format(err))

#SQL command INSERT INTO _ VALUES _ (ON DUPLICATE KEY UPDATE _, when pkeys != None)
def insert(table, entries, db_config=TEST_CONFIG, db_name=DATABASE_NAME, pkeys=None):
	conn = mysql.connector.connect(**db_config, database=db_name)
	cursor = conn.cursor()
	try:
		cols = entries[0].__dict__.keys()
		for entry in entries:
			cmd_template = (
				"INSERT INTO " + table + " " + enclose(cols,"``","()") +
				" VALUES " + enclose(cols,["%(",")s"],"()")
				)
			#cols_nokey is empty if all entry keys are primary keys, no duplicate command necessary
			if pkeys:
				cols_nokey = [col for col in cols if col not in pkeys]
				cmd_template += " ON DUPLICATE KEY UPDATE " + ", ".join([("`" + col + "`" + "='" + getattr(entry, col) + "'") for col in cols_nokey])
			#print(cmd_template)
			cursor.execute(cmd_template, entry.__dict__)
			conn.commit()
	except mysql.connector.Error as err:
		print("ERROR db_msql.insert(): " + format(err))
	finally:
		cursor.close()
		conn.close()

#SQL command SELECT target FROM table WHERE conditions.keys() = conditions[keys]
#conditions must be a dictionary, where keys are columns in table and values are condition values
def select(table, target_cols, conditions={}, db_config=TEST_CONFIG, db_name=DATABASE_NAME):
	conn = mysql.connector.connect(**db_config, database=db_name)
	cursor = conn.cursor()
	results = []
	try:
		cmd_template = (
			"SELECT " + ", ".join(target_cols) + " FROM " + table
			)
		if conditions:
			cmd_template += " WHERE " + " AND ".join(conjoin(list(conditions.keys()), list(conditions.values()), " = "))
		cursor.execute(cmd_template) #returns a iterator for a list of tuples. each item in the tuple corresponds to the targets
		for ret in cursor:
			results.append(ret)
	except mysql.connector.Error as err:
		print("ERROR db_msql.select(): " + format(err))
	finally:
		cursor.close()
		conn.close()
		return results

#TESTING: remove when production-ready
def show_databases(db_config=TEST_CONFIG):
	conn = mysql.connector.connect(**db_config)
	cursor = conn.cursor()
	databases = []
	try:
		cursor.execute("show databases;")
		for database in cursor:
			databases.append(database[0])
	except mysql.connector.Error as err:
		print("ERROR db_msql.show_database(): " + format(err))
	finally:
		cursor.close()
		conn.close()
		return databases

#TESTING: remove when production-ready
def show_tables(db_config=TEST_CONFIG, db_name=DATABASE_NAME):
	conn = mysql.connector.connect(**db_config, database=db_name)
	cursor = conn.cursor()
	tables = []
	try:
		cursor.execute("show tables;")
		for table in cursor:
			tables.append(table[0])
	except mysql.connector.Error as err:
		print("ERROR db_msql.show_database(): " + format(err))
	finally:
		cursor.close()
		conn.close()
		return tables

#TESTING: remove when production-ready
def reset(db_config=TEST_CONFIG, db_name=DATABASE_NAME):
	conn = mysql.connector.connect(**db_config)
	cursor = conn.cursor()
	try:
		cursor.execute("DROP DATABASE " + db_name)
	except mysql.connector.Error as err:
		print("ERROR db_msql.reset(): " + format(err))
	finally:
		cursor.close()
		conn.close()