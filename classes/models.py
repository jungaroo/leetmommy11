"""table schema:
links 
id  | url
int | string  (examples:  'r11/lectures/big-o/', 'r11/lectures/express-intro' )
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class LinkHTML(db.Model):
    """Link id and the link url"""

    __tablename__ = "links"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    url = db.Column(db.String(50),
                     nullable=False,
                     unique=True)

