import requests
from bs4 import BeautifulSoup, Tag


class WebScraper:

    @classmethod
    def getIdFilteredContent(cls, url: str, id: str) -> Tag:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'lxml')
        return soup.find(id=id)
