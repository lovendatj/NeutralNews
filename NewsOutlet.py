import re
import string
import requests as req

from datetime import date
from bs4 import BeautifulSoup, SoupStrainer

import nltk
from nltk.corpus import stopwords
from nltk import tokenize 

from wordcloud import WordCloud
import matplotlib.pyplot as plt 

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
        parse_rst = SoupStrainer(['title','h1','h3','p','meta'])
        articles = []
        for url in self.articles_url:
            soup = BeautifulSoup(req.get(url).content, 'lxml', parse_only=parse_rst)
            author = soup.find('meta',property="article:author")
            if author is not None:
                articles.append(Article(url, author['content'], soup.find('title').text, soup.text))
            else:
                articles.append(Article(url, None, soup.find('title').text, soup.text))
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
    def __init__(self, url, publisher, title, text):
        self.url    = url
        self.title  = title
        self.text   = text.lower()
        self.publ   = publisher
    def clean_text(self):   
        if(self.text is None):
            return
        self.remove_html()
        self.tokenize(remove_punc=True)
        self.remove_stopwords()
    

    def remove_html(self):
        tag_regex = re.compile('<.*?>')
        self.text = re.sub(tag_regex,'', self.text)

    def tokenize(self, remove_punc=False):
        sentences = tokenize.sent_tokenize(self.text)
        tokenizer = tokenize.RegexpTokenizer(r'\w+')
        text = []
        for sentence in sentences: 
            if remove_punc:
                text.append(tokenizer.tokenize(sentence))
            else:
                text.append(tokenize.word_tokenize(sentence))
        self.text = text

    def remove_punctuation(self, text):
        return text.translate(text.maketrans("", "", string.punctuation))                
        
    ## Words must be tokenized before remove_stopwords() is called
    def remove_stopwords(self):
        stop_words = set(stopwords.words('english'))
        self.text = [[word for word in sentence if not word in stop_words] for sentence in self.text]

    def word_cloud(self):
        wordcloud = WordCloud(width = 800, height = 800, 
                background_color ='white', 
                min_font_size = 10).generate(self.rawPrint()) 
        plt.figure(figsize = (8, 8), facecolor = None) 
        plt.imshow(wordcloud) 
        plt.axis("off") 
        plt.tight_layout(pad = 0) 
        plt.show() 
    def rawPrint(self):
        return ' '.join(str(word) for sentence in self.text for word in sentence)
    def tagPrint(self):
        return nltk.pos_tag(self.rawPrint())
    def __str__(self):
        return "Publisher: {}\nArticle Name: {}\nArticle Text: {}\nURL:{}".format(self.publ, self.title, self.text, self.url)