from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

import time
import json
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString

from rich.console import Console
from rich.table import Table

console = Console()

def format(text, fmt, save=False):
    try:
        if fmt == "json": 
            if save: return json.dumps(text, indent=4)
            return json.dumps(text)
        elif fmt == "xml":
            result = parseString(dicttoxml(text, custom_root="results", attr_type=False)) 
            if save: return result.toprettyxml()
            return result.toxml()
    except Exception as e:
        print(e)
        return ""
    
class Scraper:
    def __init__(self, query):
        chrome_opts = webdriver.ChromeOptions()
        chrome_opts.add_argument('--headless')
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_opts)
        self.query = query
        self.results = []

    def search_google(self, n_pages=1, timeout=None, save=False, filename=None, fmt="json"):
        driver = self.driver
        results = []
        for p in range(1, n_pages+1):
            url = "http://www.google.com/search?q=" + self.query + "&start=" + str((p-1)*10)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source,'lxml')
            s = soup.select('.yuRUbf')
            heads = soup.select('h3')
            for i in range(len(s)):
                results.append({'title': heads[i].getText(), 'link': s[i].a.get('href')})
            if timeout is not None:
                time.sleep(timeout)
        self.results = results

        fmt_data = format(self.results, fmt, save)
        if save:
            if not filename:
                raise Exception("Filename not set")
            f = open(filename+'.'+fmt, 'w')
            f.write(fmt_data)
            f.close()
            print(f"Written Results for query: {self.query} at {filename}.{fmt}")
            return f"{filename}.{fmt}"
        return fmt_data
    
    def search_yahoo(self, n_pages=1, timeout=None, save=False, filename=None, fmt="json"):
        driver = self.driver
        results = []

        url = f'https://search.yahoo.com/search/?p={self.query}'
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "lxml")

        titles = soup.find_all('h3')
        
        for title in titles:
            lnk = title.find('a')
            if lnk is not None and len(lnk) != 0:
                href_lnk = lnk.get('href')
                if title.span is not None:
                    title.span.decompose()
                results.append({'title': title.getText() , 'link': href_lnk})
                
        self.results = results
        fmt_data = format(self.results, fmt, save)
        if save:
            if not filename:
                raise Exception("Filename not set")
            f = open(filename+'.'+fmt, 'w')
            f.write(fmt_data)
            f.close()
            print(f"Written Results for query: {self.query} at {filename}.{fmt}")
            return f"{filename}.{fmt}"
        return fmt_data

    def __del__(self):
        self.driver.quit()
    
def serialize(data, from_fmt="json"):
    try:
        if from_fmt == "json": return json.loads(data)
    except Exception as e:
        print(e)
        return []
    return []

def print_table(data, fmt="json"):
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("#", style="dim", width=6)
    table.add_column("Title", min_width=20)
    table.add_column("Link", min_width=20)

    for idx, result in enumerate(data, start=1):
        table.add_row(str(idx), result['title'], result['link'])
    
    console.print(table)

def main():
    s = Scraper('Amarendra Bahubali')

    f = s.search_yahoo(fmt='json')
    s_data = serialize(f)
    print_table(s_data)
    

if __name__ == '__main__':
    main()