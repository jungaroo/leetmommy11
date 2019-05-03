from Classes.WordSearch import WordSearcher
from Classes.DBConnector import DBConnector
from secret import MONGO_DB_URI

class WordSearcherDB(WordSearcher):

    def __init__(self, base_url : str, dbConnector, cohort):

        super().__init__(base_url)
        self.dbC = dbConnector
        self.cohort = cohort
        

    def get_links_with_word_DB(self, word: str):


        COLLECTION_NAME = 'links'
        SEACH_QUERY = {'cohort':self.cohort,'search':word}

        ## if search word + self.cohort exist in DB then look up from db and return results
        RECORD_IN_DB = self.dbC.isRecordInCollection(COLLECTION_NAME,SEACH_QUERY)
        if RECORD_IN_DB:
            record = self.dbC.isRecordInCollection(COLLECTION_NAME,SEACH_QUERY)
            return record.get('result')
        else: 
            links = super().get_links_with_word(word)
            record = {"cohort": self.cohort,
                            "search": word,
                            "result": links}
            idd = self.dbC.addToCollection(COLLECTION_NAME, record)

            return links        

    def get_code_snips_with_word_DB(self, word: str):

             
        COLLECTION_NAME = 'code_snips'
        SEACH_QUERY = {'cohort':self.cohort,'search':word}

        ## if search word + self.cohort exist in DB then look up from db and return results
        RECORD_IN_DB = self.dbC.isRecordInCollection(COLLECTION_NAME,SEACH_QUERY)
        if RECORD_IN_DB:
            record = self.dbC.isRecordInCollection(COLLECTION_NAME,SEACH_QUERY)
            return record.get('result')
        else: 
            code_snips = super().get_pre_links_with_word(word)
            record = {"cohort": self.cohort,
                            "search": word,
                            "result": code_snips}
            idd = self.dbC.addToCollection(COLLECTION_NAME, record)

            return code_snips 

    def get_lecture_pages_DB(self, word: str):

             
        COLLECTION_NAME = 'lecture_pages'
        SEACH_QUERY = {'cohort':self.cohort,'search':word}

        ## if search word + self.cohort exist in DB then look up from db and return results
        RECORD_IN_DB = self.dbC.isRecordInCollection(COLLECTION_NAME,SEACH_QUERY)
        if RECORD_IN_DB:
            record = self.dbC.isRecordInCollection(COLLECTION_NAME,SEACH_QUERY)
            return record.get('result')
        else: 
            lecture_pages = super().get_lecture_pages(word)
            record = {"cohort": self.cohort,
                            "search": word,
                            "result": lecture_pages}
            idd = self.dbC.addToCollection(COLLECTION_NAME, record)

            return lecture_pages 

