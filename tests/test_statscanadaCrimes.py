#python3 -m unittest tests.test_statscanadaCrimes

import unittest

import modules.webscraper.statsCanada_crime as scCrime

###############
### Globals ###
###############

PATH = "resources/crime_statistics/"
FILE1 = "statscan_crime_canada.csv"
FILE2 = "statscan_crime_bc.csv"
LOCATION1 = "Canada"
LOCATION2 = ["British Columbia", "Burnaby", "Vancouver", "Surrey", "New Westminster", "Richmond"]

#############
### Tests ###
#############

class Test_statscanadaCrimes(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.crimes1 = scCrime.get_reports(PATH + FILE1, LOCATION1)
		cls.crimes2 = {}
		for location in LOCATION2:
			cls.crimes2[location] = scCrime.get_reports(PATH + FILE2, location)
	def test_validLocations(self):
		self.assertTrue(len(LOCATION2) == len(self.crimes2))
	def test_validCrimes(self):
		cols = self.crimes1[0].__dict__.keys()
		errors = 0
		#check for any empty fields in CrimeReport instance
		for crime in self.crimes1:
			for col in cols:
				if not getattr(crime, col):
					errors = errors + 1
		for location in self.crimes2:
			for crime in self.crimes2[location]:
				print(crime)
				for col in cols:
					if not getattr(crime, col):
						errors = errors + 1
		self.assertTrue(errors == 0)
		
if __name__ == '__main__':
	unittest.main()