#python3 -m unittest tests.test_msql

import unittest

import re
import csv
import modules.webscraper.scraper_utils as scrape
import modules.webscraper.compareSchool as cs
import modules.webscraper.statsCanada as statscan
import modules.db.msql as msql

###############
### Globals ###
###############

#Configuration File
CONF_FILE = "resources/conf/tests_config.txt"
GLOBALS = scrape.conf_processFile(CONF_FILE)

###############
### Utility ###
###############


#############
### Tests ###
#############

#these tests require the configuration files to be in proper state. Namely, all sources (in the sources configuration file)
#must correspond to a supported location (in the locations configuration file), and all source types must be accounted for.
class Test_command(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		msql.ini()
		cls.locations = msql.select_format("locations", scrape.Location, {}, GLOBALS["DB_CONFIG"], GLOBALS["DB_NAME"])
		cls.sources = msql.select_format("sources", scrape.Source, {}, GLOBALS["DB_CONFIG"], GLOBALS["DB_NAME"])
	
	#check if database exists
	def test_database(self):
		databases = msql.show_databases()
		self.assertTrue(databases.count(GLOBALS["DB_NAME"]))

	#check if all locations are in database
	def test_locations(self):
		errors = 0
		expected_locations = []
		with open(GLOBALS["CONF_PATH"] + GLOBALS["CONF_LOC_FILE"], "r", newline='', encoding='utf-8-sig') as file:
			reader = csv.DictReader(file, delimiter=',')
			for row in reader:
				loc = scrape.Location.init_dict(row)
				expected_locations.append(loc)
		for location in expected_locations:
			if location not in self.locations:
				errors += 1
		self.assertTrue(errors == 0)
	
	#check if all sources are in databases
	#TODO: may not be needed, complete later
	def test_sources(self):
		pass
		
	@classmethod
	def tearDownClass(cls):
		msql.reset()
		
if __name__ == '__main__':
	unittest.main()