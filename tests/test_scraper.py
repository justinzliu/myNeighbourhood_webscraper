#python3 -m unittest tests.test_scraper

import unittest

import re
import csv
import modules.webscraper.scraper_utils as scrape
import modules.webscraper.compareSchool as cs
import modules.webscraper.statsCanada as statscan
import modules.db.msql as msql
import modules.webscraper.scraper as scraper

###############
### Globals ###
###############

#Configuration File
CONF_FILE = "resources/conf/tests_config.txt"
GLOBALS = scrape.conf_processFile(CONF_FILE)

#############
### Tests ###
#############

class Test_command(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		msql.ini()

	#@unittest.skip("testing small file")
	def test_scrapeRun(self):
		errors = 0
		scraper.scrape_all_test()
		self.assertTrue(errors == 0)

	@classmethod
	def tearDownClass(cls):
		#msql.reset()
		pass
		
if __name__ == '__main__':
	unittest.main()