from flask import Flask, request, render_template, redirect,jsonify
from Classes.WordSearch import WordSearcher, BASE_URL, BASE_LINKS
# from models import db, connect_db, User, Post, Tag, PostTag
# from sqlalchemy import desc
# from notes_search import BASE_URL
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
    """Render Landing page"""
    return render_template("codesnips.html")

@app.route('/codeSnipSearch')
def list_snipit_links():

    search_word = request.args.get('search-word', None).lower()

    checks = [request.args.get('r11', False), request.args.get('r10', False), request.args.get('r9', False), request.args.get('r8', False)]

    all_links = {}

    for c in checks:
        if c:
            if memo2.get((c,search_word)):
                all_links[c] = memo2.get((c,search_word))
            else: 
                wc = WordSearcher(BASE_LINKS.get(c))
                links = wc.get_links_search_only_pre(search_word)
                memo2[(c,search_word)] = links
                all_links[c] = links
            
    return jsonify(lecture_links=all_links)

@app.route('/orlandoSearch')
def list_lecture_links():
    """Retrun all lecture links with word"""

    search_word = request.args.get('search-word', None).lower()

    checks = [request.args.get('r11', False), request.args.get('r10', False), request.args.get('r9', False), request.args.get('r8', False)]

    all_links = {}

    for c in checks:
        if c:
            if memo.get((c,search_word)):
                all_links[c] = memo.get((c,search_word))
            else: 
                wc = WordSearcher(BASE_LINKS.get(c))
                links = wc.get_links(search_word)
                memo[(c,search_word)] = links
                all_links[c] = links
            
    return jsonify(lecture_links=all_links)

