#from dir python3 -m unittest tests.test_compareSchool

import unittest

import modules.webscraper.compareSchool as cs

###############
### GLOBALS ###
###############

DRIVER_PATH = "/usr/lib/chromium-browser/chromedriver"
CITY = "Burnaby"

#############
### TESTS ###
#############

class Test_compareSchool(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.schools = cs.get_schools(CITY,DRIVER_PATH)
	def test_validSchools(self):
		cols = self.schools[0].__dict__.keys()
		errors = 0
		#check for any empty fields in School instance
		for school in self.schools:
			for col in cols:
				if not getattr(school, col):
					errors = errors + 1
		self.assertTrue(errors == 0)
	def test_schoolsScrolled(self):
		#check to see scroll function was utilized. Results must be > 10 
		self.assertTrue(len(self.schools) > 10)

if __name__ == '__main__':
	unittest.main()