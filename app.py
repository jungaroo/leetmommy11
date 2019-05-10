from flask import Flask, request, render_template, redirect, jsonify
from Classes.WordSearch import WordSearcher, BASE_URL, BASE_LINKS, COHORTS
from Classes.DBConnector import DBConnector
from Classes.WordSearchDB import WordSearcherDB
from Classes.InterviewQuestion import InterviewQSearcher
import os


MONGO_DB_URI = os.environ.get(
    'MONGO_DB_URI', False)

if not MONGO_DB_URI:
    import secret
    MONGO_DB_URI = secret.MONGO_DB_URI

app = Flask(__name__)


# Connect to DB leetmommy
dbC = DBConnector(MONGO_DB_URI,'leetmommy')


##################################################


@app.route('/')
def landing():
    """Render Search page"""
    return render_template("landing.html")

@app.route('/codesnip')
def render_code_snip_search():
    """Render CodeSnip Landing page"""
    return render_template("codeForm.html")


def _get_data(dbC,cohorts,search_word,type_of_search):
    # object that holds the results to be passsed to template
    data = {}

    # for each cohort that is checked:
    for cohort in cohorts:
        if cohort:
            #create a Word Searcher obj
            word_searcher = WordSearcherDB(BASE_LINKS.get(cohort),dbC,cohort)
            # ask Word Searcher obj to get code snips based on word search
            links = word_searcher.get_results_db(search_word,type_of_search)
            #append links to dict
            data[cohort] = links 

    return data   


@app.route('/codeSnipSearch')
def render_code_snips():

    TYPE_OF_SEARCH = 'code_snips'
    # get search word from query string
    search_word = request.args.get('search-word', None)

    # Get all the cohort links that were checked with the checkbox from the UI
    cohorts = [request.args.get(cohort, False) for cohort in COHORTS]

    # object that holds the results to be passsed to template
    data = _get_data(dbC,cohorts,search_word,TYPE_OF_SEARCH)
    
    return render_template("codeSnipsResult.html",links_and_snips=data)

@app.route('/conceptualSearch')
def render_entire_lecture_pages():

    TYPE_OF_SEARCH = 'lecture_pages'

    # get search word from query string
    search_word = request.args.get('search-word', None)

    # Get all the cohort links that were checked with the checkbox from the UI
    cohorts = [request.args.get(cohort, False) for cohort in COHORTS]

    # object that holds the results to be passsed to template
    data = _get_data(dbC,cohorts,search_word,TYPE_OF_SEARCH)

    return render_template("lecturePagesResult.html",lecture_pages=data)


@app.route('/linkSearch')
def list_lecture_links():
    """Return all lecture links with word"""

    TYPE_OF_SEARCH = 'links'

    search_word = request.args.get('search-word', None)

    cohorts = [request.args.get(cohort, False) for cohort in COHORTS]

    all_links = _get_data(dbC,cohorts,search_word,TYPE_OF_SEARCH)
            
    return render_template("codelinksResult.html",lecture_links=all_links)

@app.route('/interviewQSearch')
def list_interview_links():
    """Return all links with word"""

    search_word = request.args.get('search-word', None)

    iqs = InterviewQSearcher()
    links = iqs.getLinks(search_word)
            
    return render_template("interviewLinksResult.html",links=links)

