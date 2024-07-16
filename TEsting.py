import json

from Helpers.SqlLiteHelper import SQLiteHelper

with open('formatted_data_new.json', 'r') as file:
    data = json.loads(file.read())
new_data = []
for _, value in data.items():
    for model, sgl in value.items():
        new_data.append(sgl)
helper = SQLiteHelper('Scraped_Data.db')
helper.get_all()