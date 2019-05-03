from flask import Flask, request, render_template, redirect, jsonify
from Classes.WordSearch import WordSearcher, BASE_URL, BASE_LINKS, COHORTS
from secret import MONGO_DB_URI
from Classes.DBConnector import DBConnector
from Classes.WordSearchDB import WordSearcherDB

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

@app.route('/codeSnipSearch')
def render_code_snips():

    # get search word from query string
    search_word = request.args.get('search-word', None)

    # Get all the cohort links that were checked with the checkbox from the UI
    cohorts = [request.args.get(cohort, False) for cohort in COHORTS]

    # object that holds the results to be passsed to template
    data = {}

    # for each cohort that is checked:
    for cohort in cohorts:
        if cohort:
            #create a Word Searcher obj
            word_searcher = WordSearcherDB(BASE_LINKS.get(cohort),dbC,cohort)
            # ask Word Searcher obj to get code snips based on word search
            links = word_searcher.get_code_snips_with_word_DB(search_word)
            #append links to dict
            data[cohort] = links
    
    return render_template("codeSnipsResult.html",links_and_snips=data)

@app.route('/conceptualSearch')
def render_entire_lecture_pages():

    # get search word from query string
    search_word = request.args.get('search-word', None)

    # Get all the cohort links that were checked with the checkbox from the UI
    cohorts = [request.args.get(cohort, False) for cohort in COHORTS]

    # object that holds the results to be passsed to template
    data = {}

    # for each cohort that is checked:
    for cohort in cohorts:
        if cohort:
            #create a Word Searcher obj
            word_searcher = WordSearcherDB(BASE_LINKS.get(cohort),dbC,cohort)
            # ask Word Searcher obj to get code snips based on word search
            links = word_searcher.get_lecture_pages_DB(search_word)
            #append links to dict
            data[cohort] = links

    return render_template("lecturePagesResult.html",lecture_pages=data)


@app.route('/linkSearch')
def list_lecture_links():
    """Return all lecture links with word"""

    search_word = request.args.get('search-word', None)

    cohorts = [request.args.get(cohort, False) for cohort in COHORTS]

    all_links = {}

    for cohort in cohorts:
        if cohort:
            word_searcher = WordSearcherDB(BASE_LINKS.get(cohort),dbC,cohort)
            links = word_searcher.get_links_with_word_DB(search_word)
            all_links[cohort] = links
            
    return render_template("codelinksResult.html",lecture_links=all_links)

