""" 
InvertedIndex is a dictionary of search term : set of doc id's
index_doc is a dictionary of doc ids: http links
"""

import nltk
from nltk.corpus import stopwords
# nltk.download('stopwords')
# nltk.download('punkt') # need to download this for tokenizer
import requests
import bs4
import string
import sqlalchemy

import asyncio
import aiohttp


def get_words_from_link(link):
    """ Grabs all the tokenized words from the link """
    response = requests.get(link);
    soup = bs4.BeautifulSoup(response.text, features='html5lib')
    text = soup.get_text()

    tokens = nltk.word_tokenize(text)
    non_words = [*stopwords.words('english'), *string.punctuation]
    filtered_words = [word.lower() for word in tokens if word not in non_words]

    return filtered_words

def add_words_to_invindex(invindex, words, link_id):
    """Adds a list of words into the inverted index (dictionary) """
    for word in words:
        # First time seeing the word
        if word not in invindex:
            invindex[word] = {link_id}
        else:
            invindex[word].add(link_id)
    



### HELPERS
def get_lecture_links_from_table_of_contents(base_url):
    """Returns all the lecture links as an array of strings """
        
    # Go the the main links page
    response = requests.get(base_url)
    soup = bs4.BeautifulSoup(response.text, features='html5lib')

    # First grab all the href links for the lectures
    html_links = soup.find_all('a', href=True)
    links = [a['href'] for a in html_links if not a['href'].endswith('.zip')][1:]

    return links

def make_sql_query(base_url):
    """ Creates the SQL query """
    links = get_lecture_links_from_table_of_contents('http://curric.rithmschool.com/r11/lectures/')

    
    values = (", ".join([f"('{link}')" for link in links]))
    
    return f" INSERT INTO links (url) VALUES {values} "

if __name__ == "__main__":
    pass


    

