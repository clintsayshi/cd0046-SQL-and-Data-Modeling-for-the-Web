#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.policy import default
import json
import dateutil.parser
import babel
from flask import Flask, jsonify, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from pytz import timezone
from forms import *
import sys
import datetime
from models import db, Artist,Venue,Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
    date = dateutil.parser.parse(value, ignoretz=True)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
  else:
    date = value
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  recent_v = Venue.query.order_by(db.desc(Venue.id)).limit(10).all() 
  recent_a = Artist.query.order_by(db.desc(Artist.id)).limit(10).all() 
  return render_template('pages/home.html', recent_venues=recent_v, recent_artists=recent_a)


#  Venues
#  ----------------------------------------------------------------

""" def no_of_upcoming(venue):
  coming_shows = []
  for show in venue.shows:
    if(show.start_time > datetime.datetime.today()):
      coming_shows.append(show)
  return len(coming_shows) """

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.distinct(Venue.city, Venue.state).all()
  data = []
  #
  for area in venues:
    area_venues = Venue.query.filter_by(state=area.state).filter_by(city=area.city).all()
    venue_data = []
    for venue in area_venues:
        venue_data.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(Show.query.filter(Show.venue_id == venue.id).filter(Show.start_time > datetime.datetime.today()).all())
        })
    data.append({
        "city": area.city,
        "state": area.state,
        "venues": venue_data
    })
  
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  query = request.form['search_term']
  search_results = Venue.query.filter(Venue.name.ilike('%' + query + '%')).all()

  venues = []
  # 
  for v in search_results:
    upcoming_shows = []
    upcoming_shows = Show.query.filter(Show.venue_id == v.id).filter(Show.start_time > datetime.datetime.today()).all()
    # 
    current = {
      "id": v.id,
      "name": v.name,
      "num_upcoming_shows": len(upcoming_shows),
    }
    venues.append(current)

  response={
    "count": len(venues),
    "data": venues
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  #
  v = Venue.query.get(venue_id)
  if v == None:
    abort(404)
  #
  upcoming_shows = []
  past_shows = []
  # 
  og_upcoming_shows = Show.query.filter(Show.venue_id == venue_id).filter(Show.start_time > datetime.datetime.today()).all()
  og_past_shows = Show.query.filter(Show.venue_id == venue_id).filter(Show.start_time < datetime.datetime.today()).all()
  for show in og_upcoming_shows:
    temp = {
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time,
    }
    upcoming_shows.append(temp)
  for show in og_past_shows:
    temp = {
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time,
    }
    past_shows.append(temp)
 
  data = {
    "id": v.id,
    "name": v.name,
    "genres": v.genres,
    "city": v.city,
    "phone":v.phone,
    "state": v.state,
    "address": v.address,
    "website": v.website_link,
    "facebook_link": v.facebook_link,
    "image_link": v.image_link,
    "seeking_talent": v.seeking_talent,
    "seeking_description": v.seeking_description,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count":len(upcoming_shows),
  }

  data1={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  }
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  form = VenueForm()
  try:
    # create a Venue object
    v = Venue(
      name = request.form['name'],
      city = request.form['city'],
      state = request.form['state'],
      address = request.form['address'],
      phone = request.form['phone'],
      facebook_link = request.form['facebook_link'],
      website_link = request.form['website_link'],
      image_link = request.form['image_link'],
      genres = request.form.getlist('genres'),
      seeking_talent = form.seeking_talent.data,
      seeking_description = request.form['seeking_description'],
    )
    # add to session and commit to db
    db.session.add(v)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  # on successful db insert, flash success
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>/delete', methods=[ 'GET'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    v = Venue.query.filter_by(id=venue_id).first()
    db.session.delete(v)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
    error = True
  finally:
    db.session.close()
  if error:
    flash("Failed to delete venue")
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  data1 = []
  for a in artists:
    data1.append({
      "id": a.id,
      "name": a.name,
    })

  return render_template('pages/artists.html', artists=data1)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  #
  query = request.form['search_term']
  search_results = Artist.query.filter(Artist.name.ilike('%' + query + '%')).all()
  #
  artists = []
  # 
  for a in search_results:
    #
    upcoming_shows = []
    upcoming_shows = Show.query.filter(Show.artist_id == a.id).filter(Show.start_time > datetime.datetime.today()).all()
    # 
    current = {
      "id": a.id,
      "name": a.name,
      "num_upcoming_shows": len(upcoming_shows),
    }
    artists.append(current)
  
  response={
    "count": len(search_results),
    "data": artists
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  a = Artist.query.get(artist_id)
  if a == None:
    abort(404)
  
  upcoming_shows = []
  past_shows = []
  # 
  og_upcoming_shows = Show.query.filter(Show.artist_id == artist_id).filter(Show.start_time > datetime.datetime.today()).all()
  og_past_shows = Show.query.filter(Show.artist_id == artist_id).filter(Show.start_time < datetime.datetime.today()).all()
  #
  for show in og_upcoming_shows:
    temp = {
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time,
    }
    upcoming_shows.append(temp)
  for show in og_past_shows:
    temp = {
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time,
    }
    past_shows.append(temp)
 
  data = {
    "id": a.id,
    "name": a.name,
    "genres": a.genres,
    "city": a.city,
    "phone":a.phone,
    "state": a.state,
    "website": a.website_link,
    "facebook_link": a.facebook_link,
    "image_link": a.image_link,
    "seeking_venue": a.seeking_venue,
    "seeking_description": a.seeking_description,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count":len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: populate form with fields from artist with ID <artist_id>
  current_artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=current_artist)
  return render_template('forms/edit_artist.html', form=form, artist=current_artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()
  error = False
  if request.method == 'POST':
    try:
      Artist.query.filter_by(id=artist_id).update({
        Artist.name: request.form['name'],
        Artist.city: request.form['city'],
        Artist.state: request.form['state'],
        Artist.phone: request.form['phone'],
        Artist.seeking_description: request.form['seeking_description'],
        Artist.facebook_link: request.form['facebook_link'],
        Artist.website_link: request.form['website_link'],
        Artist.image_link: request.form['image_link'],
        Artist.genres: request.form.getlist('genres'),
        Artist.seeking_venue: form.seeking_venue.data
      })
      # commit artist updates
      db.session.commit()
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
      if error:
        print("Couldnt update")

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # TODO: populate form with values from venue with ID <venue_id>
  current_venue = Venue.query.get(venue_id)
  form = VenueForm(obj=current_venue)
  return render_template('forms/edit_venue.html', form=form, venue=current_venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()
  error = False
  if request.method == 'POST':
    try:
      print(request.form)
      Venue.query.filter_by(id=venue_id).update({
        Venue.name: request.form['name'],
        Venue.city: request.form['city'],
        Venue.state: request.form['state'],
        Venue.address: request.form['address'],
        Venue.phone: request.form['phone'],
        Venue.seeking_description: request.form['seeking_description'],
        Venue.facebook_link: request.form['facebook_link'],
        Venue.website_link: request.form['website_link'],
        Venue.image_link: request.form['image_link'],
        Venue.genres: request.form.getlist('genres'),
        Venue.seeking_talent: form.seeking_talent.data
      })
      # commit venue updates
      db.session.commit()
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
      if error:
        print("Couldnt update")
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm()
  error = False
  try:
    a = Artist(
      name = request.form['name'],
      city = request.form['city'],
      state = request.form['state'],
      phone = request.form['phone'],
      facebook_link = request.form['facebook_link'],
      website_link = request.form['website_link'],
      image_link = request.form['image_link'],
      genres = request.form.getlist('genres'),
      seeking_venue = form.seeking_venue.data,
      seeking_description = request.form['seeking_description'],
    )
    db.session.add(a)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  
  # on successful db insert, flash success
  if error == True:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  print(Show.query.all())
  shows = Show.query.all()
  data = []
  #
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  try:
    s = Show(artist_id = request.form['artist_id'],
      venue_id =request.form['venue_id'],
      start_time = request.form['start_time']
    )
    db.session.add(s)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  # on successful db insert, flash success
  if error:
    flash('An error occurred. Show could not be listed.')
  else:
    flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  #return render_template('pages/home.html')
  return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
""" if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) """

