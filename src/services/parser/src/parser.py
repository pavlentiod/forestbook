import requests
from bs4 import BeautifulSoup
from pandas import DataFrame

from src.services.parser.src.SFR_parse import SFR_parsing
from src.services.parser.src.SPORT_ORG_parse import SO_parsing
from src.services.parser.src.WinOrient_parse import SI_parsing
from src.services.parser.src.utils import bs


def parse_event(page: BeautifulSoup) -> (DataFrame, dict):
    title = str(page.find('title'))
    if 'WinOrient' in title:
        return SI_parsing(page)
    elif 'SportOrg' in title:
        return SO_parsing(page)
    else:
        return SFR_parsing(page)

def web_parse(link: str) -> BeautifulSoup:
    content = ''
    if 'http' in link:
        response = requests.get(link)
        try:
            content = response.content.decode(response.apparent_encoding)
        except UnicodeEncodeError as e:
            content = ''
    soup_page = bs(content)
    return soup_page


def file_parse(data: bytes) -> BeautifulSoup:
    pass