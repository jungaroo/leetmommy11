import requests
import bs4
import asyncio
# from fuzzywuzzy import fuzz

COHORTS = ['r11', 'r10', 'r9', 'r8']
BASE_URL = "http://curric.rithmschool.com/{cohort}/lectures/"
BASE_LINKS = {cohort : BASE_URL.format(cohort=cohort) for cohort in COHORTS}

class WordSearcher:
    """Word Searcher class that uses web scraping and saved html files. """

    def __init__(self, base_url : str):
        """Initializes a WordSearcher instance 
        base_url is the link to the main page that contains all the lecture links"""
        
        self.base_url = base_url
        self.links = self._get_lecture_links()

    def get_results(self, word, COLLECTION_NAME):

        switcher = { 
            "links": self._get_links_with_word, 
            "code_snips": self._get_pre_links_with_word, 
            "lecture_pages": self._get_lecture_pages
        }
        
        # get correct function, else return function that returns []
        return asyncio.run(switcher.get(COLLECTION_NAME, lambda x : [])(word))
    
    # PRIVATE METHOD
    def _get_lecture_links(self):
        """Returns all the lecture links as an array of strings """
        
        # Go the the main links page
        response = requests.get(self.base_url)
        soup = bs4.BeautifulSoup(response.text, features='html5lib')

        # First grab all the href links for the lectures
        html_links = soup.find_all('a', href=True)
        links = [a['href'] for a in html_links if not a['href'].endswith('.zip')][1:]

        return links

    # PRIVATE METHOD
    async def _search_link_word(self, link: str, word: str, option):
        """Searches one link for the word. If it is found, returns the link, else returns None 
        Has three options:
        1) links - searches and returns just the link
        2) code_snips - searches code snippets in <pre> tags
        3) lecture pages - gets full lectures pages
        """
        
        html_text = self.get_link_html(link)

        soup = bs4.BeautifulSoup(html_text, features='html5lib')

        if option == "links": # returns (https://curric.rithmschool.com/lectures/etc/)
            if word.lower() in soup.text.lower():
                return (f"{self.base_url}{link}")
        
        elif option == "code_snips":  # returns (https://curric.rithmschool.com/lectures/etc/, <pre> codesnip </pre>)
            pre = soup.find_all('pre')   
            
            for code_snip in pre:
                if word.lower() in code_snip.text.lower():  
                    return f"{self.base_url}{link}", code_snip.text
        
        elif option == "lecture_pages": # Returns full HTML of the lecture page <html> <html>
            if word.lower() in soup.text.lower():

                full_link = f"{self.base_url}{link}"
                body = soup.find('body')
                img_tags = body.find_all('img')

                # replace img tag with full link
                for img_tag in img_tags:
                    fixed_image_link = f"{full_link}{img_tag['src']}"
                    img_tag['src'] = img_tag['src'].replace(img_tag['src'], fixed_image_link)
                
                return full_link, str(body)
        # Nothing was found
        return None

    async def _get_links_with_word(self, word: str):
        """Returns a list of all the links with that word. 
            word is the query word """

        all_results = await asyncio.gather(*[
            self._search_link_word(link, word, option="links") for link in self.links])
        
        results = [link for link in all_results if link]

        return results

    async def _get_pre_links_with_word(self, word: str):
        """Returns a list of tuples of (links, code snippets) links with that word """
             
        all_results = await asyncio.gather(*[
            self._search_link_word(link, word, option="code_snips") for link in self.links])

        results = [link for link in all_results if link]

        return results

    async def _get_lecture_pages(self, word):
        """ Returns a list of full HTML of all pages with that word """
        
        all_results = await asyncio.gather(*[
            self._search_link_word(link, word, option="lecture_pages") for link in self.links])

        results = [link for link in all_results if link]

        return results
 
        
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


if __name__ == "__main__":
        
    wc = WordSearcher("http://curric.rithmschool.com/r11/lectures/")
    s = asyncio.run(wc._get_lecture_pages("flask"))
    print(s)

