from flask import Flask, request, render_template, redirect, jsonify

from classes.wordsearch import WordSearcher, BASE_URL, BASE_LINKS, COHORTS
from classes.dbconnector import DBConnector
from classes.wordsearchdb import WordSearcherDB
from classes.interviewquestion import InterviewQSearcher


import os
import pickle

from classes.models import db, connect_db, LinkHTML
from classes.indexsearch import IndexSearcher

##################################################
# Environmental variables and app connection
##################################################

MONGO_DB_URI = os.environ.get(
    'MONGO_DB_URI', False)

if not MONGO_DB_URI:
    import secret
    MONGO_DB_URI = secret.MONGO_DB_URI

UPDATE_PASSWORD = os.environ.get('UPDATE_PASSWORD', False)

if not UPDATE_PASSWORD:
    import secret
    UPDATE_PASSWORD = secret.UPDATE_PASSWORD



##################################################
# App / DB configuration
##################################################


app = Flask(__name__)

# Connect to MongoDB for wordsearchDB - leetmommy
dbC = DBConnector(MONGO_DB_URI,'leetmommy')
# Connect to PSQL for indexed search - leetmommy
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql:///leetmommy')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
connect_db(app)
db.create_all()


##################################################
# Public Routes
##################################################

@app.route('/')
def landing():
    """Render Search page"""
    return render_template("landing.html")

@app.route('/codesnip')
def render_code_snip_search():
    """Render CodeSnip Landing page"""
    return render_template("codeForm.html")


def _get_data(dbC, cohorts, search_word, type_of_search):
    """Grabs data based on type of search using MongoDB
    Returns: 
    data, which is a dictionary of:
    {
        "r11" : list of items based on type of search,
        "r10" : ...
        etc.   
    }
    """
    # object that holds the results to be passsed to template
    data = {}

    # for each cohort that is checked:
    for cohort in cohorts:
        if cohort:
            #create a Word Searcher obj
            word_searcher = WordSearcherDB(BASE_LINKS.get(cohort), dbC, cohort)
            # ask Word Searcher obj to get code snips based on word search
            links = word_searcher.get_results_db(search_word, type_of_search)
            #append links to dict
            data[cohort] = links 

    return data   


##################################################
# Search endpoints
##################################################

@app.route('/codeSnipSearch')
def render_code_snips():

    TYPE_OF_SEARCH = 'code_snips'
    # get search word from query string
    search_word = request.args.get('search-word', None)

    # Get all the cohort links that were checked with the checkbox from the UI
    cohorts = [request.args.get(cohort, False) for cohort in COHORTS]

    # object that holds the results to be passsed to template
    data = _get_data(dbC, cohorts, search_word, TYPE_OF_SEARCH)
    
    return render_template("codeSnipsResult.html", links_and_snips=data)

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

@app.route('/indexSearch')
def list_indexed_links():
    """Return all links using the inverted index - beta version to work only on rithm 11 """
    
    search_words = request.args.get('search-word', None).split();
    
    idx_searcher = IndexSearcher()
    link_ids = idx_searcher.search(search_words)

    # Use the db to grab the link name from the ID
    links_rows = LinkHTML.query.filter(LinkHTML.id.in_(link_ids))
    
    # Render the results
    base_url = 'http://curric.rithmschool.com/r11/lectures/'
    
    if (link_ids):
        urls = [f"{base_url}{link.url}" for link in links_rows]
        all_links = { "r11" : urls }
        return render_template("codelinksResult.html",lecture_links=all_links)
    else:
        return render_template("codelinksResult.html",lecture_links={"r11":["No links found"]})

    
# Admin only route to add stuff
@app.route('/buildIndex', methods=["POST"])
def build_index():
    """ Admin route for updating the links table for id: url
    """

    # Check for the correct password to allow user to update the db
    if UPDATE_PASSWORD != request.json.get('p'):
        return jsonify({"error": "Invalid"})

    # Rebuild the index!
    try:
        base_url = 'http://curric.rithmschool.com/r11/lectures/'
        IndexSearcher.rebuild_index_pickle_file(db=db, base_url=base_url)
        return jsonify({"success": "completed"})
    except Exception as e:
        print(str(e))
        return jsonify({"failure": str(e)})

