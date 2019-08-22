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

# Password to update the Inverted Index
UPDATE_PASSWORD = os.environ.get('UPDATE_PASSWORD', False)

if not UPDATE_PASSWORD:
    import secret
    UPDATE_PASSWORD = secret.UPDATE_PASSWORD


##################################################
# App / DB configuration
##################################################


app = Flask(__name__)

# Connect to MongoDB for wordsearchDB
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
    # Dictionary that holds the results to be passsed to template
    # i.e. { "r11" : [doc1, doc2, doc3, ..] }
    data = {}

    # Go through the cohorts that were checked on the form:
    for cohort in cohorts:
        if cohort:
            word_searcher = WordSearcherDB(BASE_LINKS.get(cohort), dbC, cohort)
            links = word_searcher.get_results_db(search_word, type_of_search)
            data[cohort] = links 

    return data   


##################################################
# Search endpoints
##################################################

@app.route('/codesnip-search')
def render_code_snips():

    TYPE_OF_SEARCH = 'code_snips'
    # get search word from query string
    search_word = request.args.get('search-word', None)

    # Get all the cohort links that were checked with the checkbox from the UI
    cohorts = [request.args.get(cohort, False) for cohort in COHORTS]

    # object that holds the results to be passsed to template
    data = _get_data(dbC, cohorts, search_word, TYPE_OF_SEARCH)
    
    return render_template("codeSnipsResult.html", links_and_snips=data)

@app.route('/conceptual-search')
def render_entire_lecture_pages():

    TYPE_OF_SEARCH = 'lecture_pages'

    # get search word from query string
    search_word = request.args.get('search-word', None)

    # Get all the cohort links that were checked with the checkbox from the UI
    cohorts = [request.args.get(cohort, False) for cohort in COHORTS]

    # object that holds the results to be passsed to template
    data = _get_data(dbC,cohorts,search_word,TYPE_OF_SEARCH)

    return render_template("lecturePagesResult.html", lecture_pages=data)


@app.route('/link-search')
def list_lecture_links():
    """Return all lecture links with word"""

    TYPE_OF_SEARCH = 'links'

    search_word = request.args.get('search-word', None)

    cohorts = [request.args.get(cohort, False) for cohort in COHORTS]

    all_links = _get_data(dbC,cohorts,search_word,TYPE_OF_SEARCH)
            
    return render_template("codelinksResult.html", lecture_links=all_links)


@app.route('/interviewq-search')
def list_interview_links():
    """Return all links with word"""

    search_word = request.args.get('search-word', None)

    iqs = InterviewQSearcher()
    links = iqs.getLinks(search_word)
            
    return render_template("interviewLinksResult.html",links=links)


@app.route('/index-search')
def list_indexed_links():
    """Return all links using the inverted index - works only on rithm 11 """
    
    # Grab only the supported cohorts
    cohorts = [cohort for cohort in ['r13', 'r12', 'r11'] if request.args.get(cohort)]
    cohort = cohorts[0] if cohorts else 'r13' # We only support index search for the first one

    search_words = request.args.get('search-word', None).split();
    
    idx_searcher = IndexSearcher(cohort)
    link_ids = idx_searcher.search(search_words)

    # Use the db to grab the link name from the ID
    links_rows = LinkHTML.query.filter(LinkHTML.id.in_(link_ids))
    
    # Render the results
    base_url = f'http://curric.rithmschool.com/{cohort}/lectures/'
    
    if (link_ids):
        urls = [f"{base_url}{link.url}" for link in links_rows]
        all_links = { cohort : urls }
        return render_template("codelinksResult.html",lecture_links=all_links)
    else:
        return render_template("codelinksResult.html",lecture_links={cohort:["No links found"]})

###############################    
# Private (dev only route)
###############################
@app.route('/build-index', methods=["POST"])
def build_index():
    """ Admin route for updating the psql database table that matches ids to urls.
    POST request must have a password and the rithm cohort
    """

    # Check for the correct password to allow user to update the db
    if UPDATE_PASSWORD != request.json.get('p'):
        return jsonify({"error": "Invalid password"})
    
    cohort = request.json.get('cohort', 'r11')

    base_url = f'http://curric.rithmschool.com/{cohort}/lectures/'
      
    # Rebuild the index!
    try:
        IndexSearcher.rebuild_index_pickle_file_async(db=db, base_url=base_url, cohort=cohort)
        return jsonify({"success": f"completed building for cohort {cohort}"})
    except Exception as e:
        print(str(e))
        return jsonify({"failure": str(e)})

#### API Routes ####
@app.route('/api/ping')
def ping_api():
    return jsonify({ "status " : "success" })

@app.route('/api/index-search', methods=["GET"])
def api_search():

    search_string = request.args.get('search', None)
    cohort = request.args.get('cohort', 'r11')


    if not search_string:
        return jsonify({ "error" : "A key of 'search' is required in the args" })
    
    search_words = search_string.split()

    idx_searcher = IndexSearcher(cohort)
    
    link_ids = idx_searcher.search(search_words)

    # Use the db to grab the link name from the ID
    links_rows = LinkHTML.query.filter(LinkHTML.id.in_(link_ids))
    
    # Render the results
    base_url = f'http://curric.rithmschool.com/{cohort}/lectures/'
    
    if (link_ids):
        urls = [f"{base_url}{link.url}" for link in links_rows]
    else:
        urls = []
    
    return jsonify({"links": urls})


@app.route('/api/scrape-search', methods=["GET"])
def codesnip_search():
    
    VALID_SEARCH_TYPES = ["code_snips", "lecture_pages", "links"]
    # get search word from query string
    search_word = request.args.get('search', None)
    type_of_search = request.args.get('type', None)

    if not search_word:
        return jsonify({
            "error": f"Missing 'search' query param."
        })

    if type_of_search not in VALID_SEARCH_TYPES:
        return jsonify({
            "error": f"The 'type' query param is either missing or invalid. Must be one of {VALID_SEARCH_TYPES}"
            })

    # Get a list of all the cohorts provided
    cohort_params = request.args.get('cohorts', "").split(',')

    VALID_COHORTS = ["r11", "r10", "r9", "r8"]
    # Validate cohorts
    cohorts = [cohort for cohort in cohort_params if cohort in VALID_COHORTS]


    if not cohorts:
        return jsonify({
            "error": f"'cohorts' query param is missing or invalid. Must be comma separated string with any of these: {VALID_COHORTS}'"
        })

    # object that holds the results to be passsed to template
    data = _get_data(dbC, cohorts, search_word, type_of_search)
    
    return jsonify({"data": data })


@app.route('/api/interviewq-search', methods=["GET"])
def interview_q_search():
    search_word = request.args.get('search', None)
    iqs = InterviewQSearcher()
    name_and_links = iqs.getLinks(search_word)
    
    return jsonify({"data" : name_and_links })




