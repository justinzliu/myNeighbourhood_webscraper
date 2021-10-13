import time
from datetime import date as date

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import googlemaps

import modules.webscraper.scraper_utils as scrape

#############################
### Site Specific GLOBALS ###
#############################

#Configuration File
CONF_FILE = "resources/conf/compareSchool_config.txt"
GLOBALS = scrape.conf_processFile(CONF_FILE)

###############################
### Site Specific Functions ###
###############################

def compile_schools(location:scrape.Location, schoolType:str, tbl_entries:list):
    gmap_client = googlemaps.Client(key=GLOBALS["GMAPS_API_KEY"])
    schools = []
    for entry in tbl_entries:
        retrieved = str(date.today())
        name = entry.find(class_=GLOBALS["NAME_CLASS"]).get_text(strip=True)
        score = entry.find(class_=lambda css_class : GLOBALS["SCORE_CLASS"] in css_class).get_text(strip=True)
        rank = entry.find(class_=GLOBALS["RANK_CLASS"]).get_text(strip=True)
        address, lat, long = gmaps_geocode(", ".join((name + schoolType, location.city, location.province, location.country)), gmap_client)
        latlong = scrape.serialize_tuple((str(lat),str(long)))
        school = scrape.School(location.loc_id, retrieved, schoolType, name, score, rank, address, latlong)
        schools.append(school)
    return schools

def gmaps_geocode(location_name:str, gmap_client) -> tuple:
    results = gmap_client.geocode(location_name) #list of google map locations matching location_name sorted by most likely
    address = results[0]["formatted_address"]
    lat = results[0]["geometry"]["location"]["lat"]
    long = results[0]["geometry"]["location"]["lng"]
    return address, lat, long

def get_schools(location:scrape.Location, schoolTypes:list=["Elementary","Secondary"]) -> list:
    driver = webdriver.Chrome(GLOBALS["SELENIUM_DRIVER"])  # Optional argument, if not specified will search path.
    driver.implicitly_wait(5)
    driver.maximize_window()
    schools = []
    try:
        for schoolType in schoolTypes:
            driver.get(GLOBALS["WEBSITE"])
            #select school type, either Elementary of Secondary
            schoolTab = WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.XPATH, GLOBALS["SCHOOLTYPE_XPATH_PREFIX"] + "\"" + schoolType + "\"" + GLOBALS["SCHOOLTYPE_XPATH_SUFFIX"])))
            schoolTab.click()
            #filter schools by city name
            searchBar = WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.XPATH, GLOBALS["SEARCHBAR_XPATH"])))
            time.sleep(1) #JS that creates autofill options don't seem to load fast enough majority of the time and autoComplete options are never created
            searchBar.send_keys(location.city)
            #must select autofill option, otherwise filter may include schools outside of target
            autoComplete = WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.XPATH, GLOBALS["AUTOCOMPLETE_XPATH"])))
            autoComplete.click()
            tableBody = WebDriverWait(driver,5).until(EC.presence_of_element_located((By.XPATH, GLOBALS["TABLEBODY_XPATH"])))
            scrape.scroll_down_element(driver, tableBody, GLOBALS["GET_ELEMENT"])
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            tbl_entries = soup.find("tbody").find_all("tr")
            schools.extend(compile_schools(location, schoolType, tbl_entries))
            #print(*schools, sep="\n")
    except Exception as e:
        print('error scraping:', GLOBALS["WEBSITE"], e)
    finally:
        driver.quit()
        return schools