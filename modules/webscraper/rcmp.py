import time
import csv
from datetime import date as date

import requests as req
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import modules.webscraper.scraper_utils as scrape

#############################
### site specific GLOBALS ###
#############################

PATH = "resources/crime_statistics/"
FILE = "statscan_crime_canada.csv"

#TODO: Move City/website pair to text document in JSON format
BURNABY_REPORT = "https://burnaby.rcmp-grc.gc.ca/ViewPage.action?siteNodeId=863&languageId=1&contentId=68914"
TABLE_ELEMENT = "table"
	
TYPE = "Violations"
METRIC = "Statistics"
VALUE = "VALUE"

CRIME_CATEGORIES = ["all", "violent", "property", "traffic", "drug", "other"]
STATS_HEADERS = ["incidents", "Rate", "Percentage"]

class crimeReport:
    def __init__(self, violations, incidents, rate, change, retrieved):
    	self.violations = violations
    	self.incidents = incidents
    	self.rate = rate
    	self.change = change
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
	for key in dictionary.keys():
		pattern = re.compile(target)
		if pattern.search(key):
			return key
	return None

def compile_crimes(categories, stats_headers, reports):
	crimes = []
	for category in categories:
		report_key = get_key(category, reports)
		stats = []
		for stat in stats_headers:
			stat_key = get_key(stat, reports[report_key])
			stats.append(reports[report_key][stat_key])
		crime = crimeReport(category,stats[0],stats[1],stats[2],str(date.today()))
		crimes.append(crime)
	return crimes

#site specific definitions
def get_report(website, table_element):
	with open(PATH + FILE, "r", newline='', encoding='utf-8') as file:
		reports = {}
		reader = csv.DictReader(file, delimiter=',')
		for row in reader:
			if row[TYPE] in reports:
				reports[row[TYPE]].update({row[METRIC]:row[VALUE]})
			else:
				reports[row[TYPE]] = {row[METRIC]:row[VALUE]}
	compiled_reports = compile_crimes(CRIME_CATEGORIES, STATS_HEADERS, reports)
	print(*compiled_reports, sep="\n")
	return compiled_reports

#DEPRECIATED: attempted to generalize report finding for rcmp website, website is not uniform enough to for a generalized tool
def get_next_link(start_website, target_element, target_stringIdentifer):
	start_source = req.get(start_website)
	start_soup = BeautifulSoup(start_source.content, "html.parser")
	target_website = start_soup.find(target_element, string=target_stringIdentifer)["href"]
	return target_website
def get_crimeStats(driver_path):
	WEBSITE = 'https://www.rcmp-grc.gc.ca'
	WEBSITE_MENU = 'https://www.rcmp-grc.gc.ca/en/inc/site-menu?ajax=1' #location links are loaded with ajax, not with the rest of the HTML
	CITY_LIST = "Detachments"
	REPORT_LIST = "Crime Stat"
	REPORT = "Reports"
	TABLE_IDENTIFIER = "table table-condensed table-bordered"
	LOCATION = "British Columbia"
	CITY = "Burnaby"
	try:
		#start at index rcmp menu website, navigate to rcmp province website
		province_website = get_next_link(WEBSITE_MENU, "a", LOCATION)
		print("Province Site:", province_website)
		#start at rcmp province website, navigate to rcmp province list of cities
		cityList_website = province_website.split("/ViewPage")[0] + get_next_link(province_website, "a", re.compile(CITY_LIST))
		print("CityList Site:", cityList_website)
		#start at rcmp province list of cities, locate and navigate to city website
		cityList_source = req.get(cityList_website)
		cityList_soup = BeautifulSoup(cityList_source.content, 'html.parser')
		#TODO: some cities do not have websites, return and handle NULL case
		#no pattern or unique identifiers of HTML elements to better target website.
		cityName_tag = cityList_soup.find("strong", string=CITY)
		cityul_tag = cityName_tag.find_next_sibling("ul")
		city_website = cityul_tag.find("a", string="Website")["href"]
		print("City Site:", city_website)
		#start at city website, navigate to report website
		report_website = city_website.split("/ViewPage")[0] + get_next_link(city_website, "a", re.compile(REPORT_LIST))
		print("Report Site:", report_website)
		report_source = req.get(report_website)
		report_soup = BeautifulSoup(report_source.content, 'html.parser')
		reportName_tag = cityList_soup.find(string=re.compile(REPORT))
		print(reportName_tag)
	except Exception as e:
		print('error scraping:', WEBSITE, e)
	finally:
		return []
