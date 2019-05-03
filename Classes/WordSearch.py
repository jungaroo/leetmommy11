import requests
import bs4
import re
# from fuzzywuzzy import fuzz

COHORTS = ['r11', 'r10', 'r9', 'r8']
BASE_URL = "http://curric.rithmschool.com/{cohort}/lectures/"
BASE_LINKS = {cohort : BASE_URL.format(cohort=cohort) for cohort in COHORTS}

class WordSearcher():
    """Word Searcher class that uses web scraping and saved html files. """

    def __init__(self, base_url : str):
        """Initializes a WordSearcher instance 
        base_url is the link to the main page that contains all the lecture links"""
        
        self.base_url = base_url
    
    def get_lecture_links(self):
        """Returns all the lecture links as an array of strings """
        
        # Go the the main links page
        response = requests.get(self.base_url)
        soup = bs4.BeautifulSoup(response.text, features='html5lib')

        # First grab all the href links for the lectures
        html_links = soup.find_all('a', href=True)
        links = [a['href'] for a in html_links if not a['href'].endswith('.zip')][1:]

        return links

    def get_links_with_word(self, word: str):
        """Returns all the links with that word. 
            word is the query word """

        output = []

        links = self.get_lecture_links()

        # Search for the word in each link
        for link in links:
            response = requests.get(self.base_url + link)
            soup = bs4.BeautifulSoup(response.text, features='html5lib')
            
            if word.lower() in soup.text.lower():
                output.append(f"{self.base_url}{link}")

        return output

    def get_pre_links_with_word(self, word: str, search_func=None):
        """Returns all the links with that word """
             
        output = []

        links = self.get_lecture_links()

        # search for the word
        for link in links:

            html_text = self.get_link_html(link)
            
            soup = bs4.BeautifulSoup(html_text, features='html5lib')
            pre = soup.find_all('pre')   
            for code_snip in pre:
   
                if word.lower() in code_snip.text.lower():  
                    output.append([f"{self.base_url}{link}", code_snip.text])
        
        return output

    def get_lecture_pages(self, word):

        output = []

        # Search
        response = requests.get(self.base_url)
        soup = bs4.BeautifulSoup(response.text, features='html5lib')

        # First grab all the href links for the lectures
        html_links = soup.find_all('a', href=True)
        links = [a['href'] for a in html_links if not a['href'].endswith('.zip')][1:]

        # search for the word
        for link in links:
            html_text = self.get_link_html(link)
            
            soup = bs4.BeautifulSoup(html_text, features='html5lib')
            
            if word.lower() in soup.text.lower():

                full_link = f"{self.base_url}{link}"
                body = soup.find('body')
                img_tags = body.find_all('img')

                ## replace img tag with full link
                for img_tag in img_tags:
                    fixed_image_link = f"{full_link}{img_tag['src']}"
                    img_tag['src'] = img_tag['src'].replace(img_tag['src'], fixed_image_link)
                
                output.append((full_link, str(body)))
        
        return output

        
    

    def get_link_html(self, link : str):
        """Returns the html text from the given link.
        If the html for that text is not stored in the html folder, issue a get request and store it.
        Else read it from the html file storage.
        """

        # Remove the backslashes
        clean_link = link.replace('/', '')
        clean_base = self.base_url.replace('/','')

        # Files are stored with this format:
        file_name = f"./html/{clean_base}{clean_link}.html"

        # If file exists, just read from it
        try:
            with open(file_name, "r") as html_file: 
                html_text = html_file.read()
        # If file does not exist, issue a GET request and then store it as a file
        except FileNotFoundError:
            print("Seeing file for first time")
            response = requests.get(self.base_url + link)
            with open(file_name, "w") as o:
                print(response.text, file=o)
            html_text = response.text

        return html_text

# wc = WordSearcher("http://curric.rithmschool.com/r11/lectures/")
# wc.get_conceptual_answers('flask')