import time
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

WEBSITE = 'https://www.rcmp-grc.gc.ca'
WEBSITE_MENU = 'https://www.rcmp-grc.gc.ca/en/inc/site-menu?ajax=1' #location links are loaded with ajax, not with the rest of the HTML
CITY_LIST = "Detachments"
LOCATION = "British Columbia"
CITY = "Burnaby"

#site specific definitions

def get_crimeStats(driver_path):
	try:
		index_source = req.get(WEBSITE_MENU)
		index_soup = BeautifulSoup(index_source.content, "html.parser")
		province_website = index_soup.find("a", string=LOCATION)["href"]
		print("Province Site:", province_website)
		province_source = req.get(province_website)
		province_soup = BeautifulSoup(province_source.content, "html.parser")
		cityList_website = province_website.split("/ViewPage")[0] + province_soup.find("a", string=re.compile(CITY_LIST))["href"]
		print("CityList Site:", cityList_website)
		cityList_source = req.get(cityList_website)
		cityList_soup = BeautifulSoup(cityList_source.content, 'html.parser')
		#TODO: some cities do not have websites, return and handle NULL case
		#no pattern or unique identifiers of HTML elements to better target website.
		cityName_tag = cityList_soup.find("strong", string=CITY)
		cityul_tag = cityName_tag.find_next_sibling("ul")
		city_website = cityul_tag.find("a", string="Website")["href"]
		print("City Site:", city_website)
	except Exception as e:
		print('error scraping:', WEBSITE, e)
	finally:
		return []
