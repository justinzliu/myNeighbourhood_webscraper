#python3 -m unittest tests.test_scraperUtils

import unittest
import csv
import time

import modules.webscraper.scraper_utils as scrape

###############
### Globals ###
###############

PATH = "resources/census_statistics/"
FILE_PROVINCIAL = "statscan_provincial.csv"
LOCATION_PROVINCIAL = ["Canada", "British Columbia"]
DATE = "2016"
FILE_INDEX = "GEO_NAME"

#################
### Functions ###
#################

def do_stuff(*things):
    thing_done = ""
    for thing in things:
        thing_done = str(thing)
    return thing_done

#############
### Tests ###
#############

class Test_statscanadaCensus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass
    @unittest.skip("testing another function")
    def test_bookmark(self):
        bookmark = scrape.bookmark(PATH + FILE_PROVINCIAL, FILE_INDEX)
        print(bookmark)
        assert(1 == 1)

if __name__ == '__main__':
    unittest.main()