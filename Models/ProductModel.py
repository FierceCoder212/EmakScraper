from bs4 import BeautifulSoup

from Models.PartsModel import PartsModel


class ProductModel:
    def __init__(self, section: str, image: str, xml: str):
        self.section = section
        self.image = image
        self.parts = self._parse_xml(xml)

    @staticmethod
    def _parse_xml(xml):
        soup = BeautifulSoup(xml, 'xml')
        maps = soup.find_all('map')
        return [PartsModel(item_number=map.get('a'), part_number=map.get('pid'),
                           description=map.get('label').replace(map.get('pid'), '').replace('|', '').strip()) for map in
                maps]
