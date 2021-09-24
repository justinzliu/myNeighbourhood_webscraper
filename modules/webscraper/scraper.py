import modules.db.msql as msql
import modules.webscraper.statsCanada as statsCanada
import modules.webscraper.compareSchool as compareSchool
import modules.webscraper.scraper_utils as scrape

def scrape_all():
    locations = msql.select_format("locations", scrape.Location)
    sources = msql.select_format("sources", scrape.Source)
    test_target = {"location": "Burnaby", "sourcetype": "school"}
    for source in sources:
       
       #function = getattr(source.source, source.method)
       #reports = function(source.arguments)
       #print(reports)
       print(source)
       