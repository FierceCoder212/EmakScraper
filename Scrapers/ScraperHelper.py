import json
import os
import re
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from Helpers.SqlLiteHelper import SQLiteHelper
from Models.CatalogModel import CatalogModel
from Models.HierarchyItemModel import HierarchyItemModel
from Models.JsonResponseModel import JsonResponseModel


class ScraperHelper:
    def __init__(self, formatted_data):
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Cookie': 'ASP.NET_SessionId=pdpso3eie1dp5u0wwwykofey; __RequestVerificationToken=hoZV54ZGhtNVAuAFqG8C8eVtUt2JOaGkOEcAqiD09IT6YPQnbzr1YaSCeRM0nGuw9PF8ZxOJ-aJfCGqiQ0gnbRQ8tPTMYQBc1-xqUwTNRhk1',
            'Referer': 'https://emak.ev-portal.com/Catalogs/Catalog',
            'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
        self.base_url = 'https://emak.ev-portal.com/'
        self.latest_model_code = 76280
        self.prev_data = formatted_data
        self.image_directory = 'Images'
        if not os.path.exists(self.image_directory):
            os.makedirs(self.image_directory)
        self.sql_helper = SQLiteHelper('Scraped_Data.db')
        self.images_data = []

    def scrape_data(self):
        catalogs = self.get_catalogs()
        for catalog in catalogs:
            print(f'Moving to catalog : {catalog}')
            if self.set_catalog(catalog.modelId):
                print(f'Going for catalog scrape : {catalog.name}')
                catalog_documents = self.scrape_catalog()
                print(f'Documents found : {len(catalog_documents)}')
                for index, document in enumerate(catalog_documents):
                    print(f'On doc : {index + 1} out of {len(catalog_documents)}')
                    sgl_code = self.get_sgl_code(document=document, catalog_name=catalog.name)
                    doc_record = self.create_doc_record(document=document, sgl_code=sgl_code)
                    print(f'Inserting records : {len(doc_record)}')
                    self.sql_helper.insert_many_records(doc_record)
        self.save_images_data()

    def save_images_data(self):
        print(f'Saving images : {len(self.images_data)}')
        with open('ImagesData.json', 'w') as images_file:
            images_file.write(json.dumps(self.images_data, indent=4))

    def request_node_data(self, _id: int = 0) -> Optional[JsonResponseModel]:
        url = urljoin(self.base_url,
                      f'Catalogs/NavigationGetData?nodeId={_id}&productSerialNumber=&productSerialNumberId=-1')
        print(f'Requesting node data for url : {url}')
        response = requests.get(url, headers=self.headers)
        print(f'Status Code : {response.status_code}')
        if response.status_code == 200:
            return JsonResponseModel(**response.json())
        else:
            print(json.dumps({
                'Error when requesting Node': {
                    'StatusCode': response.status_code,
                    'Response': response.text
                }
            }, indent=4))
        return None

    def get_catalogs(self) -> list[CatalogModel]:
        url = urljoin(self.base_url, 'Application/Home')
        response = requests.get(url, headers=self.headers)
        print(f'Status code : {response.status_code}')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            categories = soup.select('div.evj-cat')
            return [self.get_category_data(category) for category in categories]
        else:
            print(json.dumps({
                'Error when getting catalogs': {
                    'StatusCode': response.status_code,
                    'Response': response.text
                }
            }, indent=4))
        return []

    def set_catalog(self, catalog_id: int) -> bool:
        url = urljoin(self.base_url, f'Catalogs/CatalogSetCurrent?catId={catalog_id}')
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return True
        else:
            print(json.dumps({
                'Error when setting catalog': {
                    'StatusCode': response.status_code,
                    'Response': response.text
                }
            }, indent=4))
            return False

    @staticmethod
    def get_category_data(soup) -> CatalogModel:
        category_id = soup.get('data-ev-catid')
        category_name = soup.select_one('b').text
        return CatalogModel(modelId=category_id, name=category_name)

    @staticmethod
    def get_node_data(hierarchy_items: list[HierarchyItemModel], current_id=None) -> list[HierarchyItemModel]:
        parent_ids = set(item.ParentId for item in hierarchy_items)
        return [item for item in hierarchy_items if item.Id not in parent_ids and item.Id != current_id]

    def resolve_sgl_code(self, catalog_name: str, product_pid: str) -> str:
        if catalog_name in self.prev_data and product_pid in self.prev_data[catalog_name]:
            sgl_code = self.prev_data[catalog_name][product_pid]
        else:
            sgl_code = f'SGL{self.latest_model_code:010}'
            self.latest_model_code += 1
        return sgl_code

    def get_sgl_code(self, document: JsonResponseModel, catalog_name: str) -> str:
        curr_product = [doc for doc in document.Hierarchy if doc.IsSelected][0].Description
        product_name, separator, product_year = curr_product.partition('Cat.')
        product_name = product_name.strip()
        product_year = product_year.strip()
        product_pid = f'{product_name}{f' {product_year}' if product_year else ''}'
        sgl_code = self.resolve_sgl_code(catalog_name=catalog_name, product_pid=product_pid)
        return sgl_code

    def create_doc_record(self, document: JsonResponseModel, sgl_code: str) -> list[dict]:
        all_data = []
        print(f'Total product documents {len(document.ProductDocuments)}')
        for index, doc in enumerate(document.ProductDocuments):
            print(f'On product document {index + 1} out of {len(document.ProductDocuments)}')
            if doc.FileExtension == 'PNG':
                img_url = urljoin('https://emak.ev-portal.com/Catalogs', doc.FileNameFullPath)
                img_file_name = self.download_diagram(image_url=img_url, sgl_code=sgl_code, section=doc.Description)
                self.images_data.append({
                    'Url': img_url,
                    'FileName': img_file_name
                })
                soup = BeautifulSoup(doc.FileHotSpot, 'xml')
                maps = soup.find_all('map')
                json_data = [{
                    'sgl_unique_model_code': sgl_code,
                    'section': doc.Description,
                    'part_number': _map.get('pid'),
                    'description': _map.get('label').replace(_map.get('pid'), '').replace('|', '').strip(),
                    'item_number': _map.get('a'),
                    'section_diagram': img_file_name
                } for _map in maps]
                all_data.extend(json_data)
        return all_data

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Convert invalid filenames to valid filenames by replacing or removing invalid characters.
        """
        invalid_chars = r'[<>:"/\\|?*\']'
        sanitized_filename = re.sub(invalid_chars, '_', filename)
        sanitized_filename = sanitized_filename.strip()
        sanitized_filename = sanitized_filename[:255]
        return sanitized_filename

    def download_diagram(self, image_url: str, sgl_code: str, section: str) -> str:
        print(f'Downloading img at : {image_url}')
        file_name = f'{self.sanitize_filename(f'{sgl_code}-{section}')}.jpg'
        # response = requests.get(image_url, headers=self.headers)
        # if response.status_code == 200:
        #     with open(f'{self.image_directory}/{file_name}', 'wb') as file:
        #         file.write(response.content)
        # else:
        #     print(json.dumps({
        #         'Error when downloading img': {
        #             'StatusCode': response.status_code,
        #             'Response': response.text
        #         }
        #     }, indent=4))
        return file_name

    def scrape_catalog(self, node_id: int = 0) -> list[JsonResponseModel]:
        node_data = self.request_node_data(_id=node_id)
        if node_data:
            if node_data.ProductDocuments is not None:
                return [node_data]
            if hierarchy := node_data.Hierarchy:
                selected_node = [node for node in hierarchy if node.IsSelected]
                leaf_nodes: list[JsonResponseModel] = []
                if selected_node:
                    selected_node = selected_node[0]
                    children = [node for node in hierarchy if node.ParentId == selected_node.Id]
                    for child_node in children:
                        new_leaf_nodes = self.scrape_catalog(child_node.Id)
                        leaf_nodes.extend(new_leaf_nodes)
                return leaf_nodes
        return []

    def fetch_and_find_documents(self, node_id) -> list[JsonResponseModel]:
        json_model = self.request_node_data(node_id)
        if json_model:
            if json_model.ProductDocuments is not None:
                print('Products Found')
                return [json_model]
            if json_model.Hierarchy:
                nodes = self.get_node_data(json_model.Hierarchy, current_id=node_id)
                documents: list[JsonResponseModel] = []
                for sub_node in nodes:
                    sub_documents = self.fetch_and_find_documents(sub_node.Id)
                    if sub_documents:
                        documents.extend(sub_documents)
                return documents
        return []
