""" 
InvertedIndex is a plain python dictionary.
It maps:  { search_term : set of doc id's }
Search_term is just a token, and the doc ID's are the same ID's used to query in the database.
"""

import nltk
from nltk.corpus import stopwords

import requests
import bs4
import string
import sqlalchemy

import asyncio
import aiohttp
import pickle
from functools import reduce
from .decorators import deprecated

from classes.models import LinkHTML

PICKLE_FILE_PATH = 'inverted_index.pickle'

class IndexSearcher:
    """Class to represent the Index Search """

    def __init__(self):
        self.inv_index = self._load_from_pickle_file(PICKLE_FILE_PATH)

    def _load_from_pickle_file(self, path_to_pickle):
        """Loads a inverted index dictionary from the pickle file. """

        with open(PICKLE_FILE_PATH, 'rb') as handle:
            inv_index = pickle.load(handle)
            return inv_index

    def search(self, search_words):
        """Pass a list of search words, a string of search words. """

        # A list containing sets.
        # Each set corresponds to all the link id's that contain the word
        # ex: [ {2, 4, 6}, {3, 1} , {5,7,2} ]
        link_sets = []

        for search_word in search_words:

            # Empty set if the search word was not found in the inverted index
            current_ids = self.inv_index.get(search_word, [])

            # Add it to the link sets
            link_sets.append(set(current_ids))

        # Grab the intersections of all search terms
        link_ids = reduce(lambda acc, nxt: acc & nxt, link_sets)

        return link_ids

    ################################################
    # Static helper functions to rebuild the index pickle
    ###############################################

    @staticmethod
    async def fetch(session, url):
        """Async fetching of html from url  """
        async with session.get(url) as response:
            return await response.text(encoding="utf-8")

    @classmethod
    async def create_inv_indicies(cls, link, base_url, id_url, db):
        """ grabs all words from the link """
        async with aiohttp.ClientSession() as session:
            full_url = base_url + link

            html = await cls.fetch(session, full_url)
            soup = bs4.BeautifulSoup(html, features='html5lib')
            text = soup.get_text()

            tokens = nltk.word_tokenize(text)
            non_words = [*stopwords.words('english'), *string.punctuation]
            filtered_words = [word.lower()
                                for word in tokens if word not in non_words]

            inv_index = {}

            try:
                link_id = id_url[full_url]
            except KeyError:
                # link id does not exist
                print(full_url, "'s id does not exist. Creating new entry in db")
                new_link = LinkHTML(url=link)
                db.session.add(new_link)
                db.session.commit()
                link_id = LinkHTML.query.filter_by(url=link).first().id
                
            cls.add_words_to_invindex(
                invindex=inv_index,
                words=filtered_words,
                link_id=link_id)

            return inv_index

    @classmethod
    async def gather_all(cls, links, base_url, id_url, db):
        """Send all request to each link at the same time """
        kwargs = {
            "base_url" : base_url,
            "id_url": id_url,
            "db": db
        }
        all_results = await asyncio.gather(*[cls.create_inv_indicies(link=link, **kwargs) for link in links])
        results = [link_index for link_index in all_results if link_index]
        return results

    @classmethod
    def rebuild_index_pickle_file_async(cls, db, base_url):
        """Asynchronously rebuilds pickle file from scraping """
        
        # Grab all links
        base_url = "http://curric.rithmschool.com/r11/lectures/"
        links = cls.get_lecture_links_from_table_of_contents(base_url)

        # Create dictionary of URL : ids from database
        id_url = dict((base_url + link.url, link.id) for link in LinkHTML.query.all())

        # Send all requests to gather list of inverted indexes for each link 
        # [{"word1", {docid}, "word2", {docid} }, ...]
        results = asyncio.run(cls.gather_all(links, base_url, id_url, db))
        print("Done scraping all", len(results))

        # Combines all the indexes together. To be used with reduce
        def combine_index(acc, inv_index):
            """ { "word1" : {1, 2} } and { "word1" : {3}, "word2" : {2} }
            become { "word1" : {1, 2, 3}, "word2" : {2} }
            """
            for key, value in inv_index.items(): 
                acc[key] = acc[key] | value if key in acc else value
            return acc

        # Result of combining all inverted indices
        final_index = reduce(combine_index, results, {})

        # Write out the inverted index structure onto the pickle
        with open(PICKLE_FILE_PATH, 'wb') as handle:
            pickle.dump(final_index, handle, protocol=pickle.HIGHEST_PROTOCOL)

        print("Completed!")
        return 


    @staticmethod
    def add_words_to_invindex(invindex: dict, words: str, link_id: int):
        """Adds a list of words into the inverted index (dictionary).

        Parameters:
        invindex - A dictionary, mapping a word to a set of ids referring to the links that have an appearance of the word.
        words - A list of str. All the words that appear in the document referred to by the link_id
        link_id - An integer ID that is the link's ID (in the PSQL database)
        """

        for word in words:
            # First time seeing the word
            if word not in invindex:
                invindex[word] = {link_id}
            else:
                invindex[word].add(link_id)

    # HELPERS
    @staticmethod
    def get_lecture_links_from_table_of_contents(base_url):
        """Returns all the lecture links as an array of strings """

        # Go the the main links page
        response = requests.get(base_url)
        soup = bs4.BeautifulSoup(response.text, features='html5lib')

        # Grab all the href links for the lectures
        html_links = soup.find_all('a', href=True)
        links = [a['href']
                 for a in html_links if not a['href'].endswith('.zip')][1:]

        return links

    @staticmethod
    def make_sql_query():
        """Creates the SQL query for seeding the initial database, with all the lectures """
        links = get_lecture_links_from_table_of_contents(
            'http://curric.rithmschool.com/r11/lectures/')

        values = (", ".join([f"('{link}')" for link in links]))

        return f"INSERT INTO links (url) VALUES {values} "

    ###################################################
    # DEPRECATED Static helper functions to rebuild the index pickle synchronously
    ###################################################

    @deprecated
    @staticmethod
    def get_words_from_link(link):
        """Grabs all the tokenized words from the link"""
        response = requests.get(link)
        soup = bs4.BeautifulSoup(response.text, features='html5lib')
        text = soup.get_text()

        # NLTK corpus files must be specified in the nltk.txt
        # Filter words for nltk filters out any non stop words and string punctuation
        tokens = nltk.word_tokenize(text)
        non_words = [*stopwords.words('english'), *string.punctuation]
        filtered_words = [word.lower()
                          for word in tokens if word not in non_words]

        return filtered_words
    
    
    @deprecated
    @classmethod
    def rebuild_index_pickle_file(cls, db, base_url):
        """DEPRECATED - Rebuilds the index from the pickle file.
        Must be called in a view function.

        Pass in a base_url. i.e.
        http://curric.rithmschool.com/r11/lectures/
        """

        print("Rebuilding...")
        links = cls.get_lecture_links_from_table_of_contents(base_url)
        print("Here are the links", links)
        # Rebuild the inverted index from all of them
        invindex = {}
        for link in links:
            # This grabs words from the links using an NLTK tokenizer
            word = cls.get_words_from_link(base_url+link)

            # Grab the document ID based on that link
            link_row = LinkHTML.query.filter_by(url=link).first()
            if not link_row:  # Link does not exist in the database
                new_link = LinkHTML(url=link)
                db.session.add(new_link)
                db.session.commit()
                link_row = LinkHTML.query.filter_by(url=link).first()

            link_id = link_row.id

            # Add to the inverted index
            cls.add_words_to_invindex(invindex, word, link_id)

            print(f"Added {link} to the index")

        # Write out the inverted index structure onto the pickle
        with open(PICKLE_FILE_PATH, 'wb') as handle:
            pickle.dump(invindex, handle, protocol=pickle.HIGHEST_PROTOCOL)

        print("Completed!")