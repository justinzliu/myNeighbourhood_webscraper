import time
from datetime import date as date
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

WEBSITE = 'https://www.compareschoolrankings.org/'
NAME_CLASS = "school-name label"
RANK_CLASS = "flex text-xs-right field xs6"
SCORE_CLASS = "flex xs6 text-xs-right field score_color_"
GET_ELEMENT = "document.getElementsByClassName('school-list-table-card school-list-table-sidebar')[0]"

SEARCHBAR_XPATH = '//input[@id="keyword"]'
AUTOCOMPLETE_XPATH = '//div[@class="v-menu__content theme--light menuable__content__active v-autocomplete__content"]//div[@role="listitem"]'
TABLEBODY_XPATH = '//div[@id="school-map-view"]//table[@class="v-datatable v-table theme--light"]/tbody'

#generalization definitions
class School:
	#pass -1 for score and "n/a" for rank when not applicable 
	def __init__(self, city, name, score, rank, retrieved):
		self.city = city
		self.name = name
		self.score = score
		self.rank = rank
		self.retrieved = retrieved
	def __str__(self):
		return (" ".join([self.city,self.name,self.score,self.rank,self.retrieved]))

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
        print('ERROR func scroll_down_element: ', e)

#site specific definitions
def compile_schools(city,tbl_entries):
	schools = []
	for entry in tbl_entries:
		city = city
		name = entry.find(class_=NAME_CLASS).get_text(strip=True)
		score = entry.find(class_=lambda css_class : SCORE_CLASS in css_class).get_text(strip=True)
		rank = entry.find(class_=RANK_CLASS).get_text(strip=True)
		retrieved = str(date.today())
		school = School(city,name,score,rank,retrieved)
		schools.append(school)
	return schools

def get_schools(city, driver_path):
	driver = webdriver.Chrome(driver_path)  # Optional argument, if not specified will search path.
	driver.implicitly_wait(5)
	driver.maximize_window()
	schools = []
	try:
		driver.get(WEBSITE)
		#filter schools by city name
		searchBar = WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.XPATH, SEARCHBAR_XPATH)))
		#print("searchBar found")
		time.sleep(1) #javascript doesn't seem to load fast enough most of the time and autoComplete bar is never created
		searchBar.send_keys(city)
		#must select autofill option, otherwise filter may include schools outside of target
		autoComplete = WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.XPATH, AUTOCOMPLETE_XPATH)))
		autoComplete.click()
		#print("autoComplete found")
		tableBody = WebDriverWait(driver,5).until(EC.presence_of_element_located((By.XPATH, TABLEBODY_XPATH)))
		#print("tableBody found")

		scroll_down_element(driver, tableBody, GET_ELEMENT)
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

###########################################
#depreciated school information extraction#
###########################################
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