import time
import csv
from datetime import date as date
import re

import requests as req
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import modules.webscraper.scraper_utils as scrape

#############################
### Site Specific GLOBALS ###
#############################

#FILE headers of target data	
DATE = "REF_DATE"
LOCATION = "GEO"
TYPE = "Violations"
METRIC = "Statistics"
VALUE = "VALUE"
#FILE subheaders of target data
INCIDENTS_KEYWORD = "incidents"
RATE_KEYWORD = "Rate"
CHANGE_KEYWORD = "Percentage"
#target crime categories
CRIME_CATEGORIES = ["all", "violent", "property", "traffic", "drug"]

###############################
### Site Specific Functions ###
###############################

def compile_crimes(categories, reports):
	crimes = []
	for category in categories:
		report_key = scrape.get_key(category,reports)
		location = reports["location"]
		incidents = reports[report_key][scrape.get_key(INCIDENTS_KEYWORD,reports[report_key])]
		rate = reports[report_key][scrape.get_key(RATE_KEYWORD,reports[report_key])]
		change = reports[report_key][scrape.get_key(CHANGE_KEYWORD,reports[report_key])]
		year = reports["year"]
		retrieved = str(date.today())
		crime = scrape.CrimeReport(location,category,incidents,rate,change,year,retrieved)
		crimes.append(crime)
	return crimes

def get_reports(file, location):
	with open(file, "r", newline='', encoding='utf-8') as file:
		reports = {"location": location}
		reader = csv.DictReader(file, delimiter=',')
		for row in reader:
			pattern = re.compile(location,re.IGNORECASE)
			if pattern.search(row[LOCATION]):
				if row[TYPE] in reports:
					reports[row[TYPE]].update({row[METRIC]:row[VALUE]})
				else:
					reports[row[TYPE]] = {row[METRIC]:row[VALUE]}
	reports["year"] = row[scrape.get_key(DATE,row)]
	compiled_reports = compile_crimes(CRIME_CATEGORIES, reports)
	return compiled_reports

###########################
### Depreciated Methods ###
###########################
#kept for future reference

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
