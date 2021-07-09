import time
from datetime import date as date

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

WEBSITE = 'https://www.compareschoolrankings.org/'
#locate searchbar, input city, click autocomplete option
SEARCHBAR_XPATH = '//input[@id="keyword"]'
AUTOCOMPLETE_XPATH = '//div[@class="v-menu__content theme--light menuable__content__active v-autocomplete__content"]//div[@role="listitem"]'
TABLEBODY_XPATH = '//div[@id="school-map-view"]//table[@class="v-datatable v-table theme--light"]/tbody'
#container for school results, scroll function used to load all results
GET_ELEMENT = "document.getElementsByClassName('school-list-table-card school-list-table-sidebar')[0]"
#locate name, rank, and score fields
NAME_CLASS = "school-name label"
RANK_CLASS = "flex text-xs-right field xs6"
SCORE_CLASS = "flex xs6 text-xs-right field score_color_"

###############################
### Site Specific Functions ###
###############################

def compile_schools(city,tbl_entries):
    schools = []
    for entry in tbl_entries:
        city = city
        name = entry.find(class_=NAME_CLASS).get_text(strip=True)
        score = entry.find(class_=lambda css_class : SCORE_CLASS in css_class).get_text(strip=True)
        rank = entry.find(class_=RANK_CLASS).get_text(strip=True)
        retrieved = str(date.today())
        school = scrape.School(city,name,score,rank,retrieved)
        schools.append(school)
    return schools

def get_schools(driver_path, city):
	driver = webdriver.Chrome(driver_path)  # Optional argument, if not specified will search path.
	driver.implicitly_wait(5)
	driver.maximize_window()
	schools = []
	try:
		driver.get(WEBSITE)
		#filter schools by city name
		searchBar = WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.XPATH, SEARCHBAR_XPATH)))
		time.sleep(1) #JS that creates autofill options don't seem to load fast enough majority of the time and autoComplete options are never created
		searchBar.send_keys(city)
		#must select autofill option, otherwise filter may include schools outside of target
		autoComplete = WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.XPATH, AUTOCOMPLETE_XPATH)))
		autoComplete.click()
		tableBody = WebDriverWait(driver,5).until(EC.presence_of_element_located((By.XPATH, TABLEBODY_XPATH)))
		scrape.scroll_down_element(driver, tableBody, GET_ELEMENT)
		page_source = driver.page_source
		soup = BeautifulSoup(page_source, "html.parser")
		tbl_entries = soup.find("tbody").find_all("tr")
		schools = compile_schools(city,tbl_entries)
		#print(*schools, sep="\n")
	except Exception as e:
		print('error scraping:', WEBSITE, e)
	finally:
		driver.quit()
		return schools

###########################
### Depreciated Methods ###
###########################
#kept for future reference

def get_innerHTML(tbl_entries):
	innerHTMLs = []
	for entry in tbl_entries:
		text = entry.string
		innerHTMLs.append(text.rstrip('\n '))
	return innerHTMLs

def get_schoolDetails(names_lst, scores_lst, ranks_lst):
	tbl_names = soup_table.find_all(class_=NAME_CLASS)
	tbl_scores = soup_table.find_all(class_=is_score)
	tbl_ranks = soup_table.find_all(class_=RANK_CLASS)
	names = get_innerHTML(tbl_names)
	scores = get_innerHTML(tbl_scores)
	ranks = get_innerHTML(tbl_ranks)
	#put into School class