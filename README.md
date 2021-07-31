# Project Summary

## Project Objective/Goal

This is a webscraper program that builds and updates the database utilized by the myNeighbourhood application. Due to data for each locale being largely decentralized and generally with no published API, a custom scraper is necessary for each locale.

## Steps To Run Project

1. Navigating to the project directory
2. Start local mongodb with database named "MN_greaterVancouver"(default port, 27017)
3. Start local mySQL with database named "MN_greaterVancouver"(default port, 27017)
4. Start command.py
5. Use desired commands

## Commands
- scrape
scrape _1_ initiates webscraper for _1_ site. Due to each resource website using non-predictable website layouts, each scraper will need to be specifically     designed for each website 
- db
db _1_ _2_ runs command _2_ on database type _1_ (msql or mongo). Commands _2_ include init (initializes database with name _1_) 
- quit
exits application

## Technology Stack

### Application
- Linux, mySQL, MongoDB, Python
Dependencies:
- Python: beautiful soup 4, selenium webdriver, pymongo, mysql python, requests, googlemaps
- Selenium webdriver, set path to driver in command.py

## Features

- Command line interface for administrator tasks for myNeighbourhood, including: initializing databases, webscraping, and database interaction + maintenance.
