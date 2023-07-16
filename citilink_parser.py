# slow parser
from bs4 import BeautifulSoup
from dataclasses import dataclass
import requests
import json
import re


class TooManyRequestsException(Exception):
    pass


class NoDataException(Exception):
    pass


class NoSuchProductException(Exception):
    pass


class IncorrectURLException(Exception):
    pass


def validate_url(url: str):
    product_regex = r"^.*citilink.ru/product/.*"
    if re.match(product_regex, url) == None:
        raise IncorrectURLException("Provided URL is incorrect")


@dataclass
class CitilinkParser:
    
    html: str = ""
    
    def parse(self, url) -> dict:
        validate_url(url)
        self.html = requests.get(url)
        if self.html.status_code == 429:
            raise TooManyRequestsException("Too many requests on giver URL was send")
        soup = BeautifulSoup(self.html.text, "html.parser") 
        
        product_scraped = soup.find('script', attrs={"id": "__NEXT_DATA__"})
        if product_scraped == None:
            raise NoDataException("Data not found")
        product_info = json.loads(product_scraped.text)     
        
        parsed_data = {}
        empty_elements = 0
        
        name = product_info['props']['initialState']['analytics']['gtm']['events'][0]['event']['ecommerce']['detail']['products'][0]['name']
        price = product_info['props']['initialState']['analytics']['gtm']['events'][0]['event']['ecommerce']['detail']['products'][0]['price']
        
        if name == '':
            name = "Name is absent"
            empty_elements += 1
        if price == '':
            price = "Out of stock"
            empty_elements += 1
        
        if empty_elements == 2:
            raise NoSuchProductException("No product found on given URL")
        
        
        parsed_data.update({
                            "name": name,
                            "price": price,
                            })
        
        return parsed_data
