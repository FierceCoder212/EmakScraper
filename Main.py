import json

from Scrapers.ScraperHelper import ScraperHelper

with open('formatted_data_new.json', 'r') as pre_data_file:
    formatted_data = json.loads(pre_data_file.read())

helper = ScraperHelper(formatted_data)
helper.scrape_data()
