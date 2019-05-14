import requests
import bs4
import asyncio
import aiohttp
from functools import partial

COHORTS = ['r11', 'r10', 'r9', 'r8']
BASE_URL = "http://curric.rithmschool.com/{cohort}/lectures/"
BASE_LINKS = {cohort : BASE_URL.format(cohort=cohort) for cohort in COHORTS}

class WordSearcher:
    """Word Searcher class that uses web scraping and saved html files. """

    def __init__(self, base_url : str):
        """Initializes a WordSearcher instance 
        base_url is the link to the main page that contains all the lecture links"""
        
        self.base_url = base_url
        self.links = self._get_lecture_links_from_table_of_contents()


    def get_results(self, word, COLLECTION_NAME):
        """Get all search results based on collection name with the word """
    
        return asyncio.run(self.gather_links(COLLECTION_NAME, word))

    
    async def gather_links(self, option, word):
        """Returns a list of all the links/html/or codesnips with that word.  
        Word is the query word 
        Option is either "links", "code_snips" or "lecture pages """

        all_results = await asyncio.gather(*[
            self._search_link_word(link, word, option=option) for link in self.links])
        
        results = [link for link in all_results if link]

        return results

    # PRIVATE METHOD
    def _get_lecture_links_from_table_of_contents(self):
        """Returns all the lecture links as an array of strings """
        
        # Go the the main links page
        response = requests.get(self.base_url)
        soup = bs4.BeautifulSoup(response.text, features='html5lib')

        # First grab all the href links for the lectures
        html_links = soup.find_all('a', href=True)
        links = [a['href'] for a in html_links if not a['href'].endswith('.zip')][1:]

        return links


    async def fetch(self, session, url):
        """Asynchronous get request to the url """
        async with session.get(url) as response:
            return await response.text(encoding="utf-8")
            

    # PRIVATE METHOD
    async def _search_link_word(self, link: str, word: str, option):
        """Searches one link for the word. If it is found, returns the link, else returns None 
        Has three options:
        1) links - searches and returns just the link
        2) code_snips - searches code snippets in <pre> tags
        3) lecture pages - gets full lectures pages
        """
        
        async with aiohttp.ClientSession() as session:
            full_url = self.base_url + link
            html = await self.fetch(session, full_url)
            soup = bs4.BeautifulSoup(html, features='html5lib')
            
            # OPTION #1 - LINKS
            if option == "links": # returns (https://curric.rithmschool.com/lectures/etc/)
                if word.lower() in soup.text.lower():
                    return (f"{self.base_url}{link}")
            
            # OPTION #2 - CODE SNIPS
            elif option == "code_snips":  # returns (https://curric.rithmschool.com/lectures/etc/, <pre> codesnip </pre>)
                pre = soup.find_all('pre')   
                
                for code_snip in pre:
                    if word.lower() in code_snip.text.lower():  
                        print("success! found word in code_snip! for", link)
                        return f"{self.base_url}{link}", code_snip.text
            
            # OPTION #3 - LECTURES PAGES
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

 
if __name__ == "__main__":
        
    wc = WordSearcher("http://curric.rithmschool.com/r11/lectures/")
    s = asyncio.run(wc._get_links_with_word("flask"))
    print(s)

