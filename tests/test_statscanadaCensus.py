#python3 -m unittest tests.test_statscanadaCensus
#40 seconds

import unittest

import modules.webscraper.statsCanada as sc
import modules.webscraper.scraper_utils as scrape

###############
### Globals ###
###############

#Configuration File
CONF_FILE = "resources/conf/tests_config.txt"
GLOBALS = scrape.conf_processFile(CONF_FILE)
LOCATION = GLOBALS["CENSUS_LOCATION1"] + GLOBALS["CENSUS_LOCATION2"]

#############
### Tests ###
#############

class Test_statscanadaCensus(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.census = {}
		loc_id = 1
		for loc in GLOBALS["CENSUS_LOCATION1"]:
			location = scrape.Location(loc_id, GLOBALS["CRIME_COUNTRY"], GLOBALS["CRIME_PROVINCE"], loc)
			cls.census[loc] = sc.get_censusReports(GLOBALS["CENSUS_PATH"] + GLOBALS["CENSUS_FILE1"], location, GLOBALS["CENSUS_DATE"])[0]
			loc_id += 1
		for loc in GLOBALS["CENSUS_LOCATION2"]:
			location = scrape.Location(loc_id, GLOBALS["CRIME_COUNTRY"], GLOBALS["CRIME_PROVINCE"], loc)
			cls.census[loc] = sc.get_censusReports(GLOBALS["CENSUS_PATH"] + GLOBALS["CENSUS_FILE2"], location, GLOBALS["CENSUS_DATE"])[0]
			loc_id += 1

	def test_validLocations(self):
		self.assertTrue(len(LOCATION) == len(self.census))
		
	def test_validReport(self):
		cols = self.census[LOCATION[0]].__dict__.keys() #get member names for CensusReport class
		errors = 0
		#check for any empty fields in CensusReport instance
		for location in self.census:
			self.census[location].serialize()
			report = self.census[location]
			print(report)
			for col in cols:
				if not getattr(report, col):
					errors = errors + 1
		self.assertTrue(errors == 0)

if __name__ == '__main__':
	unittest.main()