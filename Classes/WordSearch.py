import requests
import bs4
import re

BASE_LINKS = {
    'r11': "http://curric.rithmschool.com/r11/lectures/",
    'r10': "http://curric.rithmschool.com/r10/lectures/",
    'r9': "http://curric.rithmschool.com/r9/lectures/",
    'r8': "http://curric.rithmschool.com/r8/lectures/",
}
BASE_URL = "http://curric.rithmschool.com/r11/lectures/"

class WordSearcher():

    def __init__(self, base_url):
        self.base_url = base_url
    
    def get_links(self, word):

        output = []

        # Search
        response = requests.get(self.base_url)
        soup = bs4.BeautifulSoup(response.text, features='html5lib')

        # First grab all the href links for the lectures
        html_links = soup.find_all('a', href=True)
        links = [a['href'] for a in html_links if not a['href'].endswith('.zip')][1:]

        # search for the word
        for link in links:
            response = requests.get(self.base_url + link)
            soup = bs4.BeautifulSoup(response.text, features='html5lib')
            if word in soup.text:  # regular expression
                # print("Try checking in:", f"{BASE_URL}{link}")
                output.append(f"{self.base_url}{link}")

        return output

    def get_links_search_only_pre(self, word):

        output = []

        # Search
        response = requests.get(self.base_url)
        soup = bs4.BeautifulSoup(response.text, features='html5lib')

        # First grab all the href links for the lectures
        html_links = soup.find_all('a', href=True)
        links = [a['href'] for a in html_links if not a['href'].endswith('.zip')][1:]

        # search for the word
        for link in links:

            clean_link = link.replace('/', '')
            clean_base = self.base_url.replace('/','')
         
            file_name = f"./html/{clean_base}{clean_link}.html"

            try:
                with open(file_name, "r") as html_file: 
                    html_text = html_file.read()
            except FileNotFoundError:
                print("Seeing file for first time")
                response = requests.get(self.base_url + link)
                with open(file_name, "w") as o:
                    print(response.text, file=o)
                html_text = response.text
            
            soup = bs4.BeautifulSoup(html_text, features='html5lib')
            pre = soup.find_all('pre')   
            for code_snip in pre:
                if word in code_snip.text:  # regular expression
                    # print("Try checking in:", f"{BASE_URL}{link}")
                    output.append((f"{self.base_url}{link}", code_snip.text))
        
        return output