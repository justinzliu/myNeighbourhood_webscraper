#python3 -m unittest tests.test_scraperUtils

import unittest
import csv
import time

import modules.webscraper.scraper_utils as scrape

###############
### Globals ###
###############

#Configuration File
CONF_FILE = "resources/conf/tests_config.txt"
GLOBALS = scrape.conf_processFile(CONF_FILE)

#################
### Functions ###
#################

#############
### Tests ###
#############

class Test_statscanadaCensus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dict = GLOBALS["DB_CONFIG"]
        cls.list = GLOBALS["CENSUS_LOCATION2"]
        cls.tup = ("1","2","3")

    #@unittest.skip("testing another function")
    def test_serializeDict(self):
        #print(self.dict)
        sDict = scrape.serialize_dict(self.dict)
        #print(sDict)
        usDict = scrape.unserialize_dict(sDict)
        #print(usDict)
        assert(len(usDict) > 2 and self.dict == usDict)

    def test_serializeList(self):
        #print(self.list)
        sList = scrape.serialize_list(self.list)
        #print(sList)
        usList = scrape.unserialize_list(sList)
        #print(usList)
        assert(len(usList) > 2 and self.list == usList)

    def test_serializeTuple(self):
        #print(self.tup)
        sTuple = scrape.serialize_tuple(self.tup)
        #print(sTuple)
        usTuple = scrape.unserialize_tuple(sTuple)
        #print(usTuple)
        assert(len(usTuple) > 2 and self.tup == usTuple)
    
    def test_unserializedListFormat(self):
        test_list = ["test1", "test2", "f.test_var", "test4"] 
        test_var = "testtest"
        #print(locals())
        new_list = scrape.unserializedList_format(test_list, locals())
        #print(new_list)
        assert(test_var == new_list[2])

if __name__ == '__main__':
    unittest.main()