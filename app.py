# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
    Flask,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for,
    abort,
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler, exception
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
import re
from operator import itemgetter
import sys

from models import *


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")
def venues():
    # TODO: replace with real venues data. --- Done
    # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    venues = Venue.query.all()
    data = []
    states_set = set()
    for venue in venues:
        states_set.add((venue.city, venue.state))

    states_set = list(states_set)
    states_set.sort(key=itemgetter(1, 0))

    actual_time = datetime.now()
    for location in states_set:
        venue_list = []
        for venue in venues:
            if (venue.city == location[0]) and (venue.state == location[1]):
                venue_shows = Show.query.filter_by(venue_id=venue.id).all()
                num_upcoming_shows = 0
                for show in venue_shows:
                    if show.start_time > actual_time:
                        num_upcoming_shows += 1

                venue_list.append(
                    {
                        "id": venue.id,
                        "name": venue.name,
                        "num_upcoming_shows": num_upcoming_shows,
                    }
                )

        data.append({"city": location[0], "state": location[1], "venues": venue_list})
    print(data)
    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():

    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. --- Done
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_type = request.form.get("search_term", "").strip()
    search_keyword = f"%{search_type}%"
    venues = Venue.query.filter(Venue.name.ilike(search_keyword)).all()
    venue_list = []
    actual_time = datetime.now()
    for venue in venues:
        venue_show = Show.query.filter_by(venue_id=venue.id).all()
        num_upcoming_shows = 0
        for show in venue_show:
            if show.start_time > actual_time:
                num_upcoming_shows += 1

        venue_list.append(
            {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": num_upcoming_shows,
            }
        )

    response = {"count": len(venues), "data": venue_list}

    return render_template(
        "pages/search_venues.html", results=response, search_term=search_type
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    venue = Venue.query.get(venue_id)
    print(venue)
    # TODO: replace with real venue data from the venues table, using venue_id --- Done

    if venue:
        genres = ((venue.genres.replace("{", "")).replace("}", "")).split(",")
        past_shows = []
        past_shows_count = 0
        upcoming_shows = []
        upcoming_shows_count = 0
        actual_time = datetime.now()
        for show in venue.shows:
            if show.start_time < actual_time:
                past_shows_count += 1
                past_shows.append(
                    {
                        "artist_id": show.artist_id,
                        "artist_name": show.artist.name,
                        "artist_image_link": show.artist.image_link,
                        "start_time": format_datetime(str(show.start_time)),
                    }
                )
            if show.start_time > actual_time:
                upcoming_shows_count += 1
                upcoming_shows.append(
                    {
                        "artist_id": show.artist_id,
                        "artist_name": show.artist.name,
                        "artist_image_link": show.artist.image_link,
                        "start_time": format_datetime(str(show.start_time)),
                    }
                )
        data = {
            "id": venue_id,
            "name": venue.name,
            "genres": genres,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": (venue.phone),
            "website": venue.website,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": past_shows_count,
            "upcoming_shows_count": upcoming_shows_count,
        }
    else:
        return redirect(url_for("index"))

    return render_template("pages/show_venue.html", venue=data)


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead ---Done

    form = VenueForm(request.form)
    # TODO: modify data to be the data object returned from db insertion ---Done
    name = form.name.data
    genres = form.genres.data
    address = form.address.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    website_link = form.website_link.data
    facebook_link = form.facebook_link.data
    seeking_talent = True if (form.seeking_talent.data == "Yes") else False
    seeking_description = form.seeking_description.data
    image_link = form.image_link.data

    if form.validate():
        error = False

        try:
            added_venue = Venue(
                name=name,
                genres=genres,
                address=address,
                city=city,
                state=state,
                phone=phone,
                website=website_link,
                facebook_link=facebook_link,
                seeking_talent=seeking_talent,
                seeking_description=seeking_description,
                image_link=image_link,
            )

            db.session.add(added_venue)
            db.session.commit()

        except Exception:
            error = True
            print(sys.exc_info())

        finally:
            db.session.close()

        if error:
            # TODO: on unsuccessful db insert, flash an error instead.
            flash("An error occurred. Venue " + name + " could not be listed.")
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
            print("Error in create_venue_submission()")
            # internal server error
            abort(500)
        else:
            # on successful db insert, flash success
            flash("Venue " + request.form["name"] + " was successfully listed!")
            return render_template("pages/home.html")

    else:
        flash(form.errors)
        return redirect(url_for("create_venue_submission"))


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):

    # TODO: Complete this endpoint for taking a venue_id, and using --- Done
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage --- Done
    venue = Venue.query.get(venue_id)
    if venue:
        error = False
        try:
            venue_name = venue.name
            db.session.delete(venue_name)
            db.session.commit()
        except exception:
            error = True
            db.session.rollback()
        finally:
            db.session.close()
        if error:
            abort(500)
        else:
            return redirect(url_for("venues"))

    else:
        return redirect(url_for("venues"))


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    # TODO: replace with real data returned from querying the database --- Done

    artists = Artist.query.order_by(Artist.name).all()

    data = []
    for artist in artists:
        data.append({"id": artist.id, "name": artist.name})
    return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. ---Done
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_keyword = request.form.get("search_term", "").strip()
    search_word = "%" + search_keyword + "%"
    artists = Artist.query.filter(Artist.name.ilike(search_word)).all()
    artist_list = []
    actual_time = datetime.now()
    for artist in artists:
        artist_show = Show.query.filter_by(artist_id=artist.id).all()
        num_upcoming_shows = 0
        for show in artist_show:
            if show.start_time > actual_time:
                num_upcoming_shows += 1

        artist_list.append(
            {
                "id": artist.id,
                "name": artist.name,
                "num_upcoming_shows": num_upcoming_shows,
            }
        )
        response = {"count": len(artists), "data": artist_list}
    return render_template(
        "pages/search_artists.html", results=response, search_term=search_keyword
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    artist = Artist.query.get(artist_id)
    print(artist)
    # TODO: replace with real artist data from the artist table, using artist_id --- Done
    if artist:
        genres = ((artist.genres.replace("{", "")).replace("}", "")).split(",")
        past_shows = []
        past_shows_count = 0
        upcoming_shows = []
        upcoming_shows_count = 0
        actual_time = datetime.now()
        for show in artist.shows:
            if show.start_time < actual_time:
                past_shows_count += 1
                past_shows.append(
                    {
                        "venue_id": show.venue_id,
                        "venue_name": show.venue.name,
                        "venue_image_link": show.venue.image_link,
                        "start_time": format_datetime(str(show.start_time)),
                    }
                )
            if show.start_time > actual_time:
                upcoming_shows_count += 1
                upcoming_shows.append(
                    {
                        "venue_id": show.venue_id,
                        "venue_name": show.venue.name,
                        "venue_image_link": show.venue.image_link,
                        "start_time": format_datetime(str(show.start_time)),
                    }
                )
        data = {
            "id": artist_id,
            "name": artist.name,
            "genres": genres,
            "city": artist.city,
            "state": artist.state,
            "phone": (artist.phone),
            "website": artist.website,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": past_shows_count,
            "upcoming_shows_count": upcoming_shows_count,
        }
    else:
        return redirect(url_for("index"))

    return render_template("pages/show_artist.html", artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)

    # TODO: populate form with fields from artist with ID <artist_id> --- Done
    if artist:
        form = ArtistForm(obj=artist)
        genres = ((artist.genres.replace("{", "")).replace("}", "")).split(",")
        artist = {
            "id": artist_id,
            "name": artist.name,
            "genres": artist.genres,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
        }
    else:
        return redirect(url_for("index"))

    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing --- Done
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form)

    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    genres = form.genres.data
    image_link = form.image_link.data
    facebook_link = form.facebook_link.data
    website = form.website_link.data
    seeking_venue = True if (form.seeking_venue.data == "Yes") else False
    seeking_description = form.seeking_description.data

    if form.validate():
        error = False

        try:
            artist = Artist.query.get(artist_id)
            artist.name = name
            artist.city = city
            artist.state = state
            artist.phone = phone
            artist.genres = genres
            artist.image_link = image_link
            artist.facebook_link = facebook_link
            artist.website = website
            artist.seeking_venue = seeking_venue
            artist.seeking_description = seeking_description

            db.session.commit()

        except Exception:
            error = True
            db.session.rollback()

        finally:
            db.session.close()

        if error:
            abort(500)
        else:
            return redirect(url_for("show_artist", artist_id=artist_id))

    else:
        return redirect(url_for("edit_artist_submission", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    # TODO: populate form with values from venue with ID <venue_id> --- Done
    venue = Venue.query.get(venue_id)
    if venue:
        form = VenueForm(obj=venue)
        genres = ((venue.genres.replace("{", "")).replace("}", "")).split(",")
        venue = {
            "id": venue_id,
            "name": venue.name,
            "genres": genres,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website": venue.website,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
        }
    else:
        return redirect(url_for("index"))

    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing --Done
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm(request.form)

    name = form.name.data
    genres = form.genres.data
    address = form.address.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    website = form.website_link.data
    facebook_link = form.facebook_link.data
    seeking_talent = True if (form.seeking_talent.data == "Yes") else False
    seeking_description = form.seeking_description.data
    image_link = form.image_link.data

    if form.validate():
        error = False
        try:
            venue = Venue.query.get(venue_id)
            venue.name = name
            venue.city = city
            venue.state = state
            venue.address = address
            venue.city = city
            venue.phone = phone
            venue.genres = genres
            venue.image_link = image_link
            venue.facebook_link = facebook_link
            venue.website = website
            venue.seeking_talent = seeking_talent
            venue.seeking_description = seeking_description

            db.session.commit()

        except Exception:
            error = True
            db.session.rollback()

        finally:
            db.session.close()

        if error:
            abort(500)
        else:
            return redirect(url_for("show_venue", venue_id=venue_id))

    else:
        return redirect(url_for("edit_venue_submission", venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead ---Done
    # TODO: modify data to be the data object returned from db insertion ---Done

    form = ArtistForm(request.form)

    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    genres = form.genres.data
    image_link = form.image_link.data
    facebook_link = form.facebook_link.data
    website = form.website_link.data
    seeking_venue = True if (form.seeking_venue.data == "Yes") else False
    seeking_description = form.seeking_description.data

    if form.validate():
        error = False

        try:
            new_artist = Artist(
                name=name,
                city=city,
                state=state,
                phone=phone,
                genres=genres,
                image_link=image_link,
                facebook_link=facebook_link,
                website=website,
                seeking_venue=seeking_venue,
                seeking_description=seeking_description,
            )

            db.session.add(new_artist)
            db.session.commit()

        except Exception:
            error = True
            print(sys.exc_info())

        finally:
            db.session.close()

        if error:

            # TODO: on unsuccessful db insert, flash an error instead. ---Done
            flash(
                "An error occurred. Artist "
                + request.form["name"]
                + " could not be listed."
            )
            abort(500)
        else:
            # on successful db insert, flash success
            flash("Artist " + request.form["name"] + " was successfully listed!")
            return render_template("pages/home.html")

    else:
        flash(form.errors)
        return redirect(url_for("create_artist_submission"))


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data. --- Done
    data = []
    shows = Show.query.all()

    for show in shows:
        data.append(
            {
                "venue_id": show.venue.id,
                "venue_name": show.venue.name,
                "artist_id": show.artist.id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": format_datetime(str(show.start_time)),
            }
        )

    return render_template("pages/shows.html", shows=data)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    form = ShowForm(request.form)

    artist_id = form.artist_id.data
    venue_id = form.venue_id.data
    actual_time = form.start_time.data

    error = False

    try:
        new_show = Show(start_time=actual_time, artist_id=artist_id, venue_id=venue_id)
        db.session.add(new_show)
        db.session.commit()

    except:
        error = True
        db.session.rollback()

    if error:
        # TODO: on unsuccessful db insert, flash an error instead.
        flash("An error occurred. Show could not be listed.")
        print("Error in create_show_submission")
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

    else:
        # on successful db insert, flash success
        flash("Show was successfully listed!")
        return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
