import time
import re

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

#################
### Functions ###
#################

class School:
	#pass -1 for score and "n/a" for rank when not applicable 
	def __init__(self, city, name, score, rank, retrieved):
		self.city = city
		self.name = name
		self.score = score
		self.rank = rank
		self.retrieved = retrieved
	def __repr__(self):
		cols = self.__dict__.keys()
		return (" ".join((col + ": " + getattr(self, col)) for col in cols))        

class CrimeReport:
	def __init__(self, location, violations, incidents, rate, change, year, retrieved):
		self.location = location
		self.violations = violations
		self.incidents = incidents
		self.rate = rate
		self.change = change
		self.year = year
		self.retrieved = retrieved
	def __repr__(self):
		cols = self.__dict__.keys()
		return (" ".join((col + ": " + getattr(self, col)) for col in cols))

def extract_table(table):
	table_rows = table.find_all("tr")
	ex_table = []
	lens = []
	for table_row in table_rows:
		row_entries = table_row.find_all(["th", "td"])
		lens.append(len(row_entries))
		ex_table.append([entry.get_text() for entry in row_entries])
	print(ex_table)
	return ex_table

def get_key(target, dictionary):
	matched_key = None
	for key in dictionary.keys():
		pattern = re.compile(target,re.IGNORECASE)
		if pattern.search(key):
			matched_key = key
			break
	return matched_key

def scroll_down_element(driver, element, getElement):
	#getElement is the javascript HTML get command to return an element. if the script returns a list, be sure to include the index
	try:
		action = ActionChains(driver)
		action.move_to_element(element).click().send_keys(Keys.SPACE)
		offset = 0; #scroll offset
		new_offset = driver.execute_script("return " + getElement + ".scrollHeight")
		while(offset < new_offset):
			action.perform()
			offset = new_offset
			time.sleep(0.5) #TODO: convert to webdriverwait.until
			new_offset = driver.execute_script("return " + getElement + ".scrollHeight")
			#print(offset, new_offset)
	except Exception as e:
		print('ERROR scroll_down_element(): ', e)
