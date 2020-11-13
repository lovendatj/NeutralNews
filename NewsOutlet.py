import re
import requests as req

from datetime import date
from bs4 import BeautifulSoup, SoupStrainer


class Website:
    def __init__(self, json_data):
        self.name   = json_data['name']
        self.url    = json_data['url']
        self.target = json_data['target_sub']
        self.parser = json_data['parser']

    def __str__(self):
        return "{} {} {}\nparser:{}".format(self.name,self.url,self.target,self.parser) 

class Outlet:
    def __init__(self, website:Website, date=None):
        self.website    = website
        self.date       = date
        if website.parser['type'] == 'sitemap':
            self.articles_url = self.read_xml()
            self.articles     = self.download_articles()
        else:
            self.articles_url = None
            self.articles     = None

    def read_xml(self):
        if self.website.parser['sitemap'] is None:
            return
        print('Reading XML:{}'.format(self.website.parser['sitemap']['sitemap_url']))
        xml_file = BeautifulSoup(req.get(self.website.parser['sitemap']['sitemap_url']).text,'lxml')

        data_url = []
        # Follows YYYY/MM/DD
        reg_ex = "(\d{4}|\d{2})[/ /.](0[1-9]|1[012])[/ /.](0[1-9]|[12][0-9]|3[01])"
        for entry in xml_file.findAll('url'):
            res = re.search(reg_ex,entry.loc.text)
            if res is not None:
                if(entry.loc is None):
                    continue
                # Filters for all links with current date, if provided 
                if self.date is not None and res.group(0) == self.date:
                    data_url.append(re.sub(r"[\n\t\s]*", "",entry.loc.text))
                # All links, if no arguments provided
                elif self.date is None:
                    data_url.append(re.sub(r"[\n\t\s]*", "",entry.loc.text))
        return data_url

    def download_articles(self):
        parse_rst = SoupStrainer(['title','h1','h3','p'])
        articles = []
        for url in self.articles_url:
            soup = BeautifulSoup(req.get(url).text, 'lxml', parse_only=parse_rst)
            articles.append(Article(url, soup.title.text, soup.text))
        return articles

    def __str__(self):
        print("News Outlet ran by {}".format(self.website.name))
    def printArticles(self):
        if(self.articles is not None):
            print("Articles From XML:{}".format(self.website.parser['sitemap']['sitemap_url']))
            for article in self.articles:
                print(article)
        else:
            print("No Articles Read")

class Article:
    def __init__(self, url, name, text):
        self.url    = url
        self.name   = name
        self.text   = text
    
    def clean_text(self):
        pass

    def download(self, path):
        pass

    def __str__(self):
        return "Article Name: {}".format(self.name)
    