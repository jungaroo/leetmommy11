import requests
import bs4


class InterviewQSearcher():
        
    def getLinks(self,search_word):

        ##Links from AD
        URLS = ['http://www.ardendertat.com/2011/','http://www.ardendertat.com/2011/page/2/','http://www.ardendertat.com/2011/page/3/'] 

        resultsArr = []

        for url in URLS:
            links = self.__getLinksFromAD(url,search_word)
            resultsArr.append(links)

        ##links from GG
        gg_links = self.__getLinksFromGG(search_word)
        resultsArr.append(gg_links)

        ## Flatten list
        flat_list = [item for sublist in resultsArr for item in sublist]
        return flat_list

    def __getLinksFromAD(self,pageUrl,search_word):

        response = requests.get(pageUrl)
        soup = bs4.BeautifulSoup(response.text, features='html5lib')

        # First grab all the href links for the lectures
        headers = soup.find_all('h2')
        filteredHeaders = [header for header in headers if search_word in header.text.lower()]

        links = [[header.text, header.findChildren('a')[0]['href']] for header in filteredHeaders]

        return links

    def __getLinksFromGG(self,search_word):
        URL = 'https://www.geeksforgeeks.org/fundamentals-of-algorithms/'

        response = requests.get(URL)
        soup = bs4.BeautifulSoup(response.text, features='html5lib')
        ol_tags = soup.find_all('ol')

        total_links = []

        for ol_tag in ol_tags:
            li_tags = ol_tag.find_all('li')
            li_filtered = [li for li in li_tags if search_word in li.text.lower()]
            links = [[li.text, li.findChildren('a')[0]['href']] for li in li_filtered]

            if links:
                total_links.append(links)

        flat_list = [item for sublist in total_links for item in sublist]
        return flat_list


# iqs = InterviewQSearcher()
# results = iqs.getLinks('tree')
# for links in results:
#     print('\n')
#     print(links)

