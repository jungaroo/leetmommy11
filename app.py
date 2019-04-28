from flask import Flask, request, render_template, redirect, jsonify
from Classes.WordSearch import WordSearcher, BASE_URL, BASE_LINKS, COHORTS

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_ECHO'] = True

# connect_db(app)

# # creates tables in db if non exist.
# db.create_all()


##################################################
memo = {}
memo2 = {}

@app.route('/')
def landing():
    """Render Landing page"""

    return render_template("landing.html")

@app.route('/codesnip')
def render_code_snip_search():
    """Render CodeSnip Landing page"""
    return render_template("codeForm.html")

@app.route('/codeSnipSearch')
def list_snipit_links():

    search_word = request.args.get('search-word', None)

    checks = [request.args.get(cohort) for cohort in COHORTS]

    all_links = {}

    for c in checks:
        if c:
            if memo2.get((c,search_word)):
                all_links[c] = memo2.get((c,search_word))
            else: 
                wc = WordSearcher(BASE_LINKS.get(c))
                links = wc.get_pre_links_with_word(search_word)
                memo2[(c,search_word)] = links
                all_links[c] = links
            
    print(all_links)
    return render_template("codes.html",links_and_snips=all_links)

@app.route('/linkSearch')
def list_lecture_links():
    """Return all lecture links with word"""

    search_word = request.args.get('search-word', None)

    checks = [request.args.get(cohort) for cohort in COHORTS]

    all_links = {}

    for c in checks:
        if c:
            if memo.get((c,search_word)):
                all_links[c] = memo.get((c,search_word))
            else: 
                wc = WordSearcher(BASE_LINKS.get(c))
                links = wc.get_links_with_word(search_word)
                memo[(c,search_word)] = links
                all_links[c] = links
            
    return render_template("codelinks.html",lecture_links=all_links)

