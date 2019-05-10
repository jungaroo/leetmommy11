import requests
import bs4


class InterviewQSearcher():
        
    def getLinks(self,search_word):

        URLS = ['http://www.ardendertat.com/2011/','http://www.ardendertat.com/2011/page/2/','http://www.ardendertat.com/2011/page/3/'] 

        resultsArr = []

        for url in URLS:
            links = self.__getLinksFromPage(url,search_word)
            resultsArr.append(links)

        flat_list = [item for sublist in resultsArr for item in sublist]
  
        return flat_list

    def __getLinksFromPage(self,pageUrl,search_word):

        response = requests.get(pageUrl)
        soup = bs4.BeautifulSoup(response.text, features='html5lib')

        # First grab all the href links for the lectures
        headers = soup.find_all('h2')
        filteredHeaders = [header for header in headers if search_word in header.text.lower()]

        links = [[header.text, header.findChildren('a')[0]['href']] for header in filteredHeaders]

        return links


# iqs = InterviewQSearcher()
# print(iqs.getLinks('tree'))

