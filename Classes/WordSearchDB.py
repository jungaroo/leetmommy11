from Classes.WordSearch import WordSearcher
from Classes.DBConnector import DBConnector
import random


class WordSearcherDB(WordSearcher):

    def __init__(self, base_url : str, dbConnector, cohort):

        super().__init__(base_url)
        self.dbC = dbConnector
        self.cohort = cohort

    def get_results_db(self, word, type_of_search):

        switcher = { 
            "links": self.get_links_with_word_DB, 
            "code_snips": self.get_code_snips_with_word_DB, 
            "lecture_pages": self.get_lecture_pages_DB
        }

        return switcher.get(type_of_search, lambda: [])(word)  
        
    def get_links_with_word_DB(self, word: str):

        COLLECTION_NAME = 'links'

        return self._get_results(word,COLLECTION_NAME)

    def get_code_snips_with_word_DB(self, word: str):
     
        COLLECTION_NAME = 'code_snips'

        return self._get_results(word,COLLECTION_NAME)

    def get_lecture_pages_DB(self, word: str):

        COLLECTION_NAME = 'lecture_pages'
        
        return self._get_results(word,COLLECTION_NAME)
    

    def _get_results(self,word,COLLECTION_NAME):

        SEACH_QUERY = {'cohort':self.cohort,'search':word}

        ## if search word + self.cohort exist in DB then look up from db and return results
        RECORD_IN_DB = self.dbC.isRecordInCollection(COLLECTION_NAME,SEACH_QUERY)
        if RECORD_IN_DB:
            record = self.dbC.isRecordInCollection(COLLECTION_NAME,SEACH_QUERY)
            self._randomizeUpdateDB(COLLECTION_NAME,SEACH_QUERY, word)
            return record.get('result')
        else: 
            resultsArr = super().get_results(word, COLLECTION_NAME)
            record = {"cohort": self.cohort,
                            "search": word,
                            "result": resultsArr}
            idd = self.dbC.addToCollection(COLLECTION_NAME, record)

            return resultsArr  


    def _randomizeUpdateDB(self,COLLECTION_NAME,SEACH_QUERY, word):
        RANDOM_INT = random.randint(0, 10)

        if RANDOM_INT == 5:
            # GET RECORD AND UPDATE
            resultsArr = super().get_results(word, COLLECTION_NAME)
            idd = self.dbC.updateToCollection(COLLECTION_NAME, SEACH_QUERY, resultsArr)
            print('YEHH YOU UPDATED DB!')

        return
    

