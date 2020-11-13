import json
import os 

from datetime import date

from NewsOutlet import Website
from NewsOutlet import Outlet

def cleanDirectory(path, *exclude):
    print("\nCleaning path: {}".format(path))
    removed = 0
    for file in os.scandir(path):
        removed = removed +1
        os.unlink(file.path)
    print("Removed {} in {}".format(removed, path))

def readFile(file_name):
    website = []
    with open(file_name) as file:
        data = json.load(file)
        for site in data['sites']:
            website.append(Website(site))
    return website

def aggrStats(news_outlets):
    total = 0
    tog = []
    for news in news_outlets:
        total = total + len(news.articles_url)
        tog.append(news.website.name + '('+str(len(news.articles_url))+') ')
    print()
    print(''.join(tog))
    print("Total Articles:", total)

def main():
    # Test Data : res/test_data.json
    # All Site  : res/sites.json
    file_name = "res/test_data.json"
    print('Reading JSON: {}\n'.format(file_name))
    file_sites = readFile(file_name)

    news_outlet = []
    date_stamp = date.today().strftime("%Y/%m/%d") 
    for ws in file_sites:
        news_outlet.append(Outlet(ws, date_stamp))
    aggrStats(news_outlet)
    cleanDirectory('res/articles/')

    for no in news_outlet:
        print(no.printArticles())    

if __name__ == "__main__":
    main()
    
    


