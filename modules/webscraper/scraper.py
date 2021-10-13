import modules.db.msql as msql
import modules.webscraper.statsCanada as statsCanada
import modules.webscraper.compareSchool as compareSchool
import modules.webscraper.scraper_utils as scrape

###############
### GLOBALS ###
###############

#Configuration File
CONF_FILE = "resources/conf/scraper_config.txt"
GLOBALS = scrape.conf_processFile(CONF_FILE)

#################
### Functions ###
#################

#scrape source by calling source.method(*source.arguments) and insert into table, vars allows strings to be used as variable names
def scrape_source(source:scrape.Source, vars:dict) -> None:
    reports = []
    function = getattr(globals()[source.source], source.method)
    args = scrape.unserialize_list(source.arguments, "\"&\"", vars)
    reports = function(*args)
    for report in reports:
        report.serialize()
    print(reports)
    msql.insert(source.type, reports, pkeys=msql.PRIMARY_KEYS[source.type])

#scrape all sources stored in sources table given a target source type
def scrape_source_byType(source:scrape.Source, locations:list) -> list:
    pass

#scrape all sources stored in sources table
def scrape_all():
    locations = msql.select_format("locations", scrape.Location)
    sources = msql.select_format("sources", scrape.Source)
    for source in sources:
       location = scrape.get_location(source.loc_id, locations)
       if location:
            scrape_source(source, {"location":location})

#DEBUG: scrape single location testing purposes
def scrape_all_test():
    locations = msql.select_format("locations", scrape.Location)
    locations = [locations[5]]
    sources = msql.select_format("sources", scrape.Source)
    for source in sources:
       location = scrape.get_location(source.loc_id, locations)
       if location:
            scrape_source(source, {"location":location})