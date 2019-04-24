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

@app.route('/')
def landing():
    """Render Landing page"""

    return render_template("landing.html")

@app.route('/orlandoSearch')
def list_lecture_links():
    """Retrun all lecture links with word"""

    search_word = request.args.get('search-word', None).lower()
    # r11 = request.args.get('r11', False)
    # r10 = request.args.get('r10', False)
    # r9 = request.args.get('r9', False)
    # r8 = request.args.get('r8', False)

    checks = [request.args.get('r11', False), request.args.get('r10', False), request.args.get('r9', False), request.args.get('r8', False)]

    all_links = {}

    for c in checks:
        if c:
            if memo.get(c):
                all_links[c] = memo.get(c)
            else: 
                wc = WordSearcher(BASE_LINKS.get(c))
                links = wc.get_links(search_word)
                memo[c] = links
                all_links[c] = links
            
    # if r11:
    #     if memo.get(r11):
    #         all_links['r11'] = memo.get(r11)
    #     else: 
    #         wc = WordSearcher(BASE_LINKS.get(r11))
    #         links = wc.get_links(search_word)
    #         memo[r11] = links
    #         all_links['r11'] = links
    
    # if r10:
    #     wc = WordSearcher(BASE_LINKS.get(r10))
    #     links = wc.get_links(search_word)
    #     all_links['r10'] = links

    # if r9:
    #     wc = WordSearcher(BASE_LINKS.get(r9))
    #     links = wc.get_links(search_word)
    #     all_links['r9'] = links

    # if r8:
    #     wc = WordSearcher(BASE_LINKS.get(r8))
    #     links = wc.get_links(search_word)
    #     all_links['r8'] = links

    return jsonify(lecture_links=all_links)

