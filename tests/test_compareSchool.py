#python3 -m unittest tests.test_compareSchool

import unittest

import modules.webscraper.compareSchool as cs
import modules.webscraper.scraper_utils as scrape

###############
### GLOBALS ###
###############

#Configuration File
CONF_FILE = "resources/conf/tests_config.txt"
GLOBALS = scrape.conf_processFile(CONF_FILE)

#############
### TESTS ###
#############

class Test_compareSchool(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.schools = {}
		for city in GLOBALS["CS_CITY"]:
			location = scrape.Location(1, GLOBALS["CS_COUNTRY"], GLOBALS["CS_PROVINCE"], city)
			cls.schools[city] = cs.get_schools(location, GLOBALS["CS_SCHOOLTYPE"])

	def test_validSchools(self):
		cols = self.schools[list(self.schools)[0]][0].__dict__.keys()
		errors = 0
		#check for any empty fields in School instance
		for loc in self.schools:
			for school in self.schools[loc]:
				for col in cols:
					if not getattr(school, col):
						errors = errors + 1
		print(self.schools, sep="\n")
		self.assertTrue(errors == 0)

	def test_schoolsScrolled(self):
		#check to see scroll function was utilized. When not scrolled, only up to 8 schools will be scraped. Make sure results are > 8 or test will wrongly fail
		errors = 0
		for loc in self.schools:
			if len(self.schools[loc]) < 7:
				errors += 1
		self.assertTrue(errors == 0)

if __name__ == '__main__':
	unittest.main()