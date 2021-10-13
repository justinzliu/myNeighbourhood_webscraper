import functools
import time
import re
import csv
from typing import Iterable

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

#################
### Functions ###
#################

@functools.total_ordering
class Location:
	def __init__(self, loc_id, country, province, city):
		self.loc_id = loc_id
		self.country = country
		self.province = province
		self.city = city

	#__init__ using 3 arguments, used for initial insertion of location into `location` table
	@classmethod
	def init_partial(cls, country, province, city):
		return cls(None, country, province, city)

	#__init__ using dictionary
	@classmethod
	def init_dict(cls, dictionary):
		if "loc_id" in dictionary:
			return cls(dictionary["loc_id"], dictionary["country"], dictionary["province"], dictionary["city"])
		else:
			return cls(None, dictionary["country"], dictionary["province"], dictionary["city"])

	def isMatch(self, other):
		return (self.country == other.country and self.province == other.province and self.city == other.city)

	def addID(self, loc_id):
		self.loc_id = loc_id

	def __repr__(self):
		members = self.__dict__.keys()
		return (" ".join((member + ": " + str(getattr(self, member)) + "\n") for member in members))
	
	def __lt__(self, other):
		#return (self.loc_id) < (other.loc_id)
		self_loc = self.country + self.province + self.city
		other_loc = other.country + other.province + other.city
		return self_loc < other_loc
	
	def __eq__(self, other):
		#return (self.loc_id == other.loc_id)
		return (self.country == other.country and self.province == other.province and self.city == other.city)

class Source:
	def __init__(self, loc_id, type, source, method, arguments):
		self.loc_id = loc_id
		self.type = type
		self.source = source
		self.method = method
		self.arguments = arguments

	#__init__ using dictionary
	@classmethod
	def init_dict(cls, loc_id, dictionary):
		return cls(loc_id, dictionary["type"], dictionary["source"], dictionary["method"], dictionary["arguments"])
	
	def __repr__(self):
		members = self.__dict__.keys()
		return (" ".join((member + ": " + str(getattr(self, member)) + "\n") for member in members))

	def __lt__(self, other):
		return (self.loc_id) < (other.loc_id)
	
	def __eq__(self, other):
		return (self.type, self.loc_id) == (other.type, other.loc_id)

class Report:
	def __init__(self, loc_id, retrieved):
		self.loc_id = loc_id
		self.retrieved = retrieved

	def serialize(self):
		raise NotImplementedError()

	def __repr__(self):
		members = self.__dict__.keys()
		return (" ".join((member + ": " + str(getattr(self, member)) + "\n") for member in members))   

class CrimeReport(Report):
	def __init__(self, loc_id, retrieved, violations, incidents, rate, change, year):
		Report.__init__(self, loc_id, retrieved)
		self.violations = violations
		self.incidents = incidents
		self.rate = rate
		self.change = change
		self.year = year

	def serialize(self):
		self.loc_id = str(self.loc_id)	

class CensusReport(Report):
	def __init__(self, loc_id, retrieved, population, ageGroups, demographics, avgAge, avgIncome, avgHouseIncome, year):
		Report.__init__(self, loc_id, retrieved)
		self.population = population
		self.ageGroups = ageGroups
		self.demographics = demographics
		self.avgAge = avgAge
		self.avgIncome = avgIncome
		self.avgHouseIncome = avgHouseIncome
		self.year = year

	def serialize(self):
		self.loc_id = str(self.loc_id)
		if type(self.ageGroups) is dict:
			self.ageGroups = serialize_dict(self.ageGroups)
		if type(self.demographics) is dict:
			self.demographics = serialize_dict(self.demographics)

class School(Report):
	def __init__(self, loc_id, retrieved, s_type, name, score, rank, address, coordinate):
		Report.__init__(self, loc_id, retrieved)
		self.name = name
		self.type = s_type
		self.score = score
		self.rank = rank
		self.address = address
		self.coordinate = coordinate

	def serialize(self):
		self.loc_id = str(self.loc_id)
		if type(self.coordinate) is tuple:
			self.coordinate = serialize_tuple(self.coordinate)

def extract_table(table:str) -> list:
	table_rows = table.find_all("tr")
	ex_table = []
	lens = []
	for table_row in table_rows:
		row_entries = table_row.find_all(["th", "td"])
		lens.append(len(row_entries))
		ex_table.append([entry.get_text() for entry in row_entries])
	print(ex_table)
	return ex_table

#search list for target and return the first match from list. match if target is found anywhere within list element
def get_key(target:str, lst:list) -> str:
	matched_key = None
	pattern = re.compile(target, re.IGNORECASE)
	for el in lst:
		if pattern.match(el):
			matched_key = el
			break
	return matched_key

#search list elements and return the first match to target. match if list element is found anywhere within target
def match_key(key:str, lst:list) -> str:
	matched_key = None
	for el in lst:
		pattern = re.compile(el, re.IGNORECASE)
		if pattern.match(key):
			matched_key = el
			break
	return matched_key

def get_location(target_id:str, locations:list) -> Location:
	location = None
	for loc in locations:
		if loc.loc_id == target_id:
			location = loc
	return location

#extract headers and remove newline and string quotes
def csv_getHeader(file:str, encoding:str="utf-8-sig") -> list:
	with open(file, "r", newline='', encoding=encoding) as file:
		headers = file.readline().split('","')
		headers[0] = headers[0].replace('"', '') #formatting: first header entry remove "
		headers[-1] = headers[-1][:-2] #formatting: last key entry must remove \n"
	return headers

#given a file and index (category that a file is sorted on), return a dictionary with the distinct elements of category as keys and tuples with the starting and ending index of its occurances
def bookmark(file:str, file_index:str) -> dict:
	references = {}
	prev_val = None
	with open(file, "r", newline='', encoding='utf-8') as file:
		reader = csv.DictReader(file, delimiter=',')
		for index, row in enumerate(reader):
			curr_val = row[file_index]
			if curr_val not in references:
				#start of a category
				references[curr_val] = [index, index]
				if prev_val and curr_val != prev_val:
					#end of previous category
					references[prev_val][1] = index
			prev_val = curr_val
		references[curr_val][1] = index #set end index to last val
	return references

#ini csv files may contain serialized lists in the form [val1&...&valn]. Once csv converted to dictionary, search values for serialized lists	
def conf_processFile(file:str) -> dict:
	processed_file = {}
	pat_list = re.compile('\[.*\]$') #pattern to find serialized lists of the form [val1&...&valn]
	pat_dict = re.compile('\{.*\}$') #pattern to find serialized dictionaries of the form {key1:val1&...&keyn:valn}
	with open(file, newline='', encoding='utf-8-sig') as file:
		for line in file:
			#if comment pattern or empty line found
			if line[0] == "#" or line[0] == "\n":
				pass
			#lines in key, value pairs
			else:
				key_val = line.split(", ", maxsplit=1)
				key = key_val[0].strip("\"")
				val = key_val[1].strip("\"\n")
				#if list pattern found
				if pat_list.match(val):
					val = unserialize_list(val)
				#if dictionary pattern found
				elif pat_dict.match(val):
					val = unserialize_dict(val)
				processed_file[key] = val
	return processed_file

#serialize list into recognized format in txt and csv config files
def serialize_list(lst:list, sep:str="\",\"", enclosure:str="") -> str:
	sList = "[\"" + sep.join(lst) + "\"]"
	if len(enclosure) == 2:
		sList = enclosure[0] + sList + enclosure[1]
	return sList

#serialize dictionary into recognized format in txt and csv config files
def serialize_dict(dictionary:dict, sep:str="\",\"", enclosure:str="") -> str:
	sDict = "{\"" + sep.join("{}\":\"{}".format(*item) for item in dictionary.items()) + "\"}"
	if len(enclosure) == 2:
		sDict = enclosure[0] + sDict + enclosure[1]
	return sDict

#serialize tuples into recognized format in txt and csv config files
def serialize_tuple(tup:tuple, sep:str="\",\"", enclosure:str="") -> str:
	sTuple = "(\"" + sep.join(tup) + "\")"
	if len(enclosure) == 2:
		sTuple = enclosure[0] + sTuple + enclosure[1]
	return sTuple

#unserialize recognized format in text and csv config files into list
def unserialize_list(sList:str, sep:str="\",\"", vars:dict={}) -> list:
	raw_list = sList.strip("[\"]")
	lst = raw_list.split(sep)
	pattern = re.compile("f.") #tag for string values to be used as variable names
	if vars:
		for index, val in enumerate(lst):
			if pattern.match(val):
				lst[index] = vars[val[2:]]
	return lst

#unserialize recognized format in text and csv config files into dictionary
def unserialize_dict(sDict:str, sep:str="\",\"") -> dict:
	dictionary = {}
	raw_dict = sDict.strip("{{\"}}")
	raw_dict = raw_dict.split(sep)
	for el in raw_dict:
		key_val = el.split("\":\"")
		dictionary[key_val[0]] = key_val[1]
	return dictionary

#unserialize recognized format for tuples, tuple values are converted to strings
def unserialize_tuple(sTuple:str, sep:str="\",\"") -> tuple:
	raw_tup = sTuple.strip("(\")")
	raw_tup = raw_tup.split(sep)
	return tuple(i for i in raw_tup)

def unserialize_value(element:str, sep:str="\",\"") -> Iterable:
	pat_list = re.compile('\[.*\]$') #pattern to find serialized lists of the form [val1&...&valn]
	pat_dict = re.compile('\{.*\}$') #pattern to find serialized dictionaries of the form {key1:val1&...&keyn:valn}
	pat_tup = re.compile('(.*)$') #pattern to find serialized tuples of the form {key1:val1&...&keyn:valn}
	uelement = []
	pass

#DEPRECIATED
#elements in list may be tagged to be used as local variables names rather than string values and will be formatted to correct values given a local variable map
def unserializedList_format(lst:list, local_vars:dict) -> list:
	fList = []
	pattern = re.compile("f.")
	for el in lst:
		if pattern.match(el):
			fList.append(local_vars[el[2:]])
		else:
			fList.append(el)
	return fList

def scroll_down_element(driver:str, element:str, getElement:str) -> None:
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