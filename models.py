from flask import Flask
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object("config")
db = SQLAlchemy(app)


# TODO: connect to a local postgresql database --- Done
migrate = Migrate(app, db)

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

# Venue Model
class Venue(db.Model):
    # Venue table name
    __tablename__ = "Venue"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate --- Done
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(120))

    shows = db.relationship("Show", backref="Venue", lazy=True)

    def __repr__(self):
        return f"<Venue ID: {self.id}, name: {self.name}>"


# Artist model
class Artist(db.Model):
    # Artist tablename
    __tablename__ = "Artist"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate --- Done
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(120))

    shows = db.relationship("Show", backref="Artist")

    past_shows = (
        db.session.query(shows)
        .join(Venue)
        .filter(shows.Artist.id == shows.artist_id)
        .filter(shows.start_time > datetime.now())
        .all()
    )

    upcoming_shows = (
        db.session.query(shows)
        .join(Venue)
        .filter(shows.Artist.id == shows.artist_id)
        .filter(shows.start_time > datetime.now())
        .all()
    )

    def __repr__(self):
        return f"<Artist ID: {self.id}, name: {self.name}>"


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration. --- Done
# Relationship table
class Show(db.Model):
    __tablename__ = "Show"

    id = db.Column(db.Integer(), primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.now())
    artist_id = db.Column(
        db.Integer(), db.ForeignKey("Artist.id", ondelete="CASCADE"), nullable=False
    )
    venue_id = db.Column(
        db.Integer(), db.ForeignKey("Venue.id", ondelete="CASCADE"), nullable=False
    )

    def __repr__(self):
        return f"<Show ID: {self.id}, start_time: {self.start_time}>"


# # To sync all the new column modules together
db.create_all()
