from flask import Flask, request, render_template, redirect, jsonify
from classes.wordsearch import WordSearcher, BASE_URL, BASE_LINKS, COHORTS
from classes.dbconnector import DBConnector
from classes.wordsearchdb import WordSearcherDB
from classes.interviewquestion import InterviewQSearcher
import os
import pickle

from classes.models import db, connect_db, LinkHTML
from classes import indexsearch


MONGO_DB_URI = os.environ.get(
    'MONGO_DB_URI', False)

if not MONGO_DB_URI:
    import secret
    MONGO_DB_URI = secret.MONGO_DB_URI

UPDATE_PASSWORD = os.environ.get('UPDATE_PASSWORD', False)

if not UPDATE_PASSWORD:
    import secret
    UPDATE_PASSWORD = secret.UPDATE_PASSWORD

app = Flask(__name__)


# Connect to DB leetmommy
dbC = DBConnector(MONGO_DB_URI,'leetmommy')


##################################################

# Connect to DB for indexed search
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI', 'postgresql:///leetmommy')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
connect_db(app)


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

@app.route('/indexSearch')
def list_indexed_links():
    """Return all links using the inverted index - beta version to work only on rithm 11 """
    search_word = request.args.get('search-word', None)

    # Open the file that will load your inverted index
    with open('inverted_index.pickle', 'rb') as handle:
        inverted_index = pickle.load(handle)

    base_url = 'http://curric.rithmschool.com/r11/lectures/'
    
    print(inverted_index)
    # Search the word through the inverted index
    link_ids = inverted_index.get(search_word, [])

    # Use the db to grab the link name from the ID
    links_rows = LinkHTML.query.filter(LinkHTML.id.in_(link_ids))
    
    if (link_ids):
        urls = [base_url + link.url for link in links_rows]
        all_links = { "r11" : urls }
        return render_template("codelinksResult.html",lecture_links=all_links)
    else:
        return render_template("codelinksResult.html",lecture_links={"r11":["No links found"]})

    

# Admin only route to add stuff
@app.route('/buildIndex', methods=["POST"])
def build_index():
    """ Admin route for updating the links table for id: url
    """

    if UPDATE_PASSWORD != request.json.get('p'):
        return jsonify({"error": "Invalid"})

    import asyncio 
    import aiohttp 
    import pickle

    base_url = 'http://curric.rithmschool.com/r11/lectures/'
    links = indexsearch.get_lecture_links_from_table_of_contents(base_url)

    # Create the inverted index from all of them 
    invindex = {}
    for link in links:
        word = indexsearch.get_words_from_link(base_url+link) # This grabs words from the links using an NLTK tokenizer
        
        # Grab the document ID based on that link
        link_row = LinkHTML.query.filter_by(url=link).first()
        if not link_row: # Link does not exist in the database
            new_link = LinkHTML(url=link)
            db.session.add(new_link)
            db.session.commit()
            link_row = LinkHTML.query.filter_by(url=link).first()

        link_id = link_row.id

        # Add to the inverted index
        indexsearch.add_words_to_invindex(invindex, word, link_id)
        print("Done with: ", link_id)
    
    # Write out the inverted index structure onto the pickle 
    with open('inverted_index.pickle', 'wb') as handle:
        pickle.dump(invindex, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    print("saved!")
    return jsonify({"stuff": "completed"})

