#python3 -m unittest tests.test_rcmp

import unittest

import modules.webscraper.rcmp as rcmp

###############
### GLOBALS ###
###############

DRIVER_PATH = "/usr/lib/chromium-browser/chromedriver"
LOCATION = "British Columbia"

#############
### TESTS ###
#############

class Test_compareSchool(unittest.TestCase):
	#@classmethod
	#def setUpClass(cls):
	#	cls.schools = cs.get_schools(CITY,DRIVER_PATH)
	def test_validCrimes(self):
		#rcmp.get_crimeStats(DRIVER_PATH)
		rcmp.get_report("1","2")
		self.assertTrue(1 > 0)

if __name__ == '__main__':
	unittest.main()