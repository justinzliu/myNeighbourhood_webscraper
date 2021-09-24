#python3 -m unittest tests.test_statscanadaCrimes
#431 seconds

import unittest

import modules.webscraper.statsCanada as statscan
import modules.webscraper.scraper_utils as scrape

###############
### Globals ###
###############

#Configuration File
CONF_FILE = "resources/conf/tests_config.txt"
GLOBALS = scrape.conf_processFile(CONF_FILE)
LOCATION = GLOBALS["CRIME_LOCATION1"] #+ GLOBALS["CRIME_LOCATION2"]

#############
### Tests ###
#############

class Test_statscanadaCrimes(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.crimes = {}
		loc_id = 1
		for loc in GLOBALS["CRIME_LOCATION1"]:
			location = scrape.Location(loc_id, GLOBALS["CRIME_COUNTRY"], GLOBALS["CRIME_PROVINCE"], loc)
			cls.crimes[loc] = statscan.get_crimeReports(GLOBALS["CRIME_PATH"] + GLOBALS["CRIME_FILE1"], location, GLOBALS["CRIME_DATE"])
			loc_id += 1
		#for location in GLOBALS["CRIME_LOCATION2"]:
		#	cls.crimes[location] = statscan.get_crimeReports(GLOBALS["CRIME_PATH"] + GLOBALS["CRIME_FILE2"], GLOBALS["CRIME_PROVINCE"], location, GLOBALS["CRIME_DATE"])
		#   loc_id += 1

	def test_validLocations(self):
		self.assertTrue(len(LOCATION) == len(self.crimes))

	def test_validCrimes(self):
		members = self.crimes[LOCATION[0]][0].__dict__.keys()
		errors = 0
		#check for any empty fields in CrimeReport instance
		for location in self.crimes:
			for crime in self.crimes[location]:
				print(crime)
				for member in members:
					if not getattr(crime, member):
						errors = errors + 1
		self.assertTrue(errors == 0)
		
if __name__ == '__main__':
	unittest.main()