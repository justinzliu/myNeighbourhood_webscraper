import time
import csv
from datetime import date as date
import re
import json

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

#Configuration File
CONF_FILE = "resources/conf/statscan_config.txt"
GLOBALS = scrape.conf_processFile(CONF_FILE)

###############################
### Site Specific Functions ###
###############################

#returns a list of crimeReports for each key in CRIME_CATEGORIES
def compile_crimes(categories, reports):
    crimes = []
    for category in categories:
        report_key = scrape.get_key(category,reports.keys()) #crime report based on CRIME_CATEGORIES
        retrieved = str(date.today())
        incidents = reports[report_key][scrape.get_key(GLOBALS["CRIME_INCIDENTS_KEYWORD"],reports[report_key].keys())]
        rate = reports[report_key][scrape.get_key(GLOBALS["CRIME_RATE_KEYWORD"],reports[report_key].keys())]
        change = reports[report_key][scrape.get_key(GLOBALS["CRIME_CHANGE_KEYWORD"],reports[report_key].keys())]
        crime = scrape.CrimeReport(reports["loc_id"], retrieved, category, incidents, rate, change, reports["year"])
        crimes.append(crime)
    return crimes

def compile_census(report):
    keys = list(GLOBALS["CENSUS_CATEGORIES"].keys())
    retrieved = str(date.today())
    population = report[keys[0]]
    ageGroups_dict = report[keys[1]]
    demographics_dict = report[keys[2]]
    #delete Totals from both groups
    del ageGroups_dict[scrape.get_key(GLOBALS["CENSUS_TOTALS"], ageGroups_dict.keys())]
    del demographics_dict[scrape.get_key(GLOBALS["CENSUS_TOTALS"], demographics_dict.keys())] #remove Total count
    del demographics_dict[scrape.get_key(GLOBALS["CENSUS_TOTALS"], demographics_dict.keys())] #remove Total visible minority count
    #serialize dictionary to JSON
    ageGroups = json.dumps(ageGroups_dict)
    demographics = json.dumps(demographics_dict)
    avgAge = report[keys[3]]
    avgIncome = report[keys[4]]
    avgHouseIncome = report[keys[5]]
    censusReport = scrape.CensusReport(report["loc_id"], retrieved, population, ageGroups, demographics, avgAge, avgIncome, avgHouseIncome, report["year"])
    return censusReport

def process_data(file, location, date, categories, location_head, date_head, type_head, metric_head, value_head):
    cat = categories.copy()
    with open(file, "r", newline='', encoding='utf-8-sig') as file:
        headers = file.readline().split('","')
        headers[0] = headers[0].replace('"', '') #formatting: first key entry remove "
        headers[-1] = headers[-1][:-3] #formatting: last key entry must remove \n"
        file.seek(0)
        reports = {"loc_id": location.loc_id, "year": date}
        reader = csv.DictReader(file, delimiter=',')
        location_key = scrape.get_key(location_head, headers)
        date_key = scrape.get_key(date_head, headers)
        type_key = scrape.get_key(type_head, headers)
        metric_key = scrape.get_key(metric_head, headers)
        value_key = scrape.get_key(value_head, headers)
        subhead_key = None #stores key value when subheaders are present
        num_subcategories = 0
        for row in reader:
            location_pattern = re.compile(location.city,re.IGNORECASE)
            if location_pattern.search(row[location_key]) and row[date_key] == date:
                key = scrape.match_key(row[type_key], cat.keys())
                if num_subcategories > 0:
                    reports[subhead_key].update({row[metric_key]:row[value_key]})
                    if num_subcategories == 1:
                        #remove key when all subheaders in category are found
                        cat.pop(subhead_key)
                    num_subcategories = num_subcategories - 1
                elif key:
                    num_subcategories = int(cat[key])
                    if num_subcategories == 0:
                        #no subheaders
                        reports[key] = row[value_key]
                        cat.pop(key)
                    else:
                        #nest subheaders under a header as a dictionary
                        subhead_key = key
                        reports[key] = {row[metric_key]:row[value_key]}
    return reports

def get_crimeReports(file, location, cr_date):
    reports = process_data(file, location, cr_date, GLOBALS["CRIME_CATEGORIES"], GLOBALS["CRIME_LOCATION"], GLOBALS["CRIME_DATE"], GLOBALS["CRIME_TYPE"], GLOBALS["CRIME_METRIC"], GLOBALS["CRIME_VALUE"])
    compiled_reports = compile_crimes(GLOBALS["CRIME_CATEGORIES"], reports)
    return compiled_reports

def get_censusReports(file, location, cr_date):
    report = process_data(file, location, cr_date, GLOBALS["CENSUS_CATEGORIES"], GLOBALS["CENSUS_LOCATION"], GLOBALS["CENSUS_DATE"], GLOBALS["CENSUS_TYPE"], GLOBALS["CENSUS_TYPE"], GLOBALS["CENSUS_VALUE"])
    census_report = compile_census(report)
    return census_report



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
