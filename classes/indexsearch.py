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

pickle_index = {
    'r11': 'r11.pickle',
    'r12': 'r12.pickle',
    'r13': 'r13.pickle',
}

class IndexSearcher:
    """Class to represent the Index Search
    self.inv_index : A dictionary with mapping of words : set of doc ID's, loaded from a pickle file
    """

    def __init__(self, cohort):
        pickle_file_path = pickle_index[cohort]
        self.inv_index = self._load_from_pickle_file(pickle_file_path)

    def _load_from_pickle_file(self, path_to_pickle):
        """Loads a inverted index dictionary from the pickle file. """

        with open(path_to_pickle, 'rb') as handle:
            inv_index = pickle.load(handle)
            return inv_index

    def search(self, search_words):
        """ Pass in list of a string of words to search for. """

        # A list of sets, where each set contains all link id's (of the lecture notes) that contain that word, where
        # search_words[i] corresponds to link_sets[i]
        # e.g. search_words = [ "database", "query", "sql"] may return:
        # [ {2, 4, 6}, {3, 1} , {5,7,2} ] , meaning the word 'database' was found in docs #2, 4 and 6
        link_sets = []

        for search_word in search_words:
            
            search_word = search_word.lower()
            
            # Empty set if the search word was not found in the inverted index
            current_ids = self.inv_index.get(search_word, [])

            # Add it to the link sets
            link_sets.append(set(current_ids))

        # Grab the intersections of all search terms
        link_ids = reduce(lambda acc, nxt: acc & nxt, link_sets)

        return link_ids

    ################################################
    # Static (private) helper functions to rebuild the index pickle
    ###############################################

    @staticmethod
    async def fetch(session, url):
        """Helper. An asynchronous get request to a URL. Returns the get request response as text. """
        async with session.get(url) as response:
            return await response.text(encoding="utf-8")

    @classmethod
    async def create_inv_indicies(cls, lecture_title, base_url, id_url, db):
        """Grabs all words in the document's html text of the given link.
        Returns an inverted index built from that document.
        
        base_url : A string , like: 'http://curric.rithmschoo.com/r13/lectures/' 
        link :  A string, the lecture title
        """
        async with aiohttp.ClientSession() as session:
            full_url = base_url + lecture_title

            # Fetch raw HTML text
            html = await cls.fetch(session, full_url)
            soup = bs4.BeautifulSoup(html, features='html5lib')
            text = soup.get_text()

            # Filter out non-token words using nltk's corpus. Words such as 'of', 'the', 'but'.
            tokens = nltk.word_tokenize(text)
            non_words = [*stopwords.words('english'), *string.punctuation]
            filtered_words = [word.lower()
                              for word in tokens if word not in non_words]

            # Add the full lecture title and split lecture title into the index list
            filtered_words.extend([*lecture_title.split('-'), lecture_title])

            inv_index = {}

            try:
                link_id = id_url[full_url]
            except KeyError:  # link does not currently exist in our database.
                print(full_url, "'s id does not exist. Creating new entry in db")
                new_link = LinkHTML(url=lecture_title)
                db.session.add(new_link)
                db.session.commit()
                link_id = LinkHTML.query.filter_by(url=lecture_title).first().id

            cls.add_words_to_invindex(
                invindex=inv_index,
                words=filtered_words,
                link_id=link_id)

            return inv_index

    @classmethod
    async def gather_all(cls, links, base_url, id_url, db):
        """Sends all request to each rithm lecture link at the same time.
        params: links - array of strings of urls to append to the base_url.
        id_url: 
        db: SQLAlchemy database object so that the id's can be inserted into the db
        """

        kwargs = {
            "base_url": base_url,
            "id_url": id_url,
            "db": db
        }

        all_results = await asyncio.gather(
            *[cls.create_inv_indicies(lecture_title=lecture_title, **kwargs) for lecture_title in links]
        )
        results = [link_index for link_index in all_results if link_index]
        return results

    @classmethod
    def rebuild_index_pickle_file_async(cls, db, base_url, cohort):
        """Asynchronously rebuilds pickle file from scraping """

        # Grab all links
        links = cls.get_lecture_links_from_table_of_contents(base_url)

        # Create dictionary of URL : ids from database
        id_url = dict((base_url + link.url, link.id)
                      for link in LinkHTML.query.all())

        # Send all requests to gather list of inverted indexes for each link
        # [{"word1", {docid}, "word2", {docid} }, ...]
        results = asyncio.run(cls.gather_all(links, base_url, id_url, db))
        print("Done scraping all", len(results))

        # Combines two indexes together. To be used with reduce
        def combine_index(acc, inv_index):
            """ { "word1" : {1, 2} } and { "word1" : {3}, "word2" : {2} }
            become { "word1" : {1, 2, 3}, "word2" : {2} }
            """
            for key, value in inv_index.items():
                # If the key exists in both, combine them, else initialize a new entry
                acc[key] = (acc[key] | value) if key in acc else value
            return acc

        # Result of combining all inverted indices
        final_index = reduce(combine_index, results, {})

        pickle_file_path = pickle_index[cohort]

        # Write out the inverted index structure onto the pickle
        with open(pickle_file_path, 'wb') as handle:
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
        """Creates the SQL query for seeding the initial database, with all the lectures. One time use, probably never use again. """
        links = get_lecture_links_from_table_of_contents(
            'http://curric.rithmschool.com/r11/lectures/')

        values = (", ".join([f"('{link}')" for link in links]))

        return f"INSERT INTO links (url) VALUES {values} "
