import os
from flask import Flask, flash, request, redirect, session, url_for, render_template, jsonify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(64)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'login'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/login'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

mysql = MySQL(app)

client_id = 'e277fd6395144b87a080712a4bfd11c2'
client_secret = '229559746a76424e97d05f6a7ad6f3f5'
redirect_uri = 'http://localhost:5000/callback'
scope = 'user-read-private user-read-email'

cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True

)

class SongLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artist = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    user_email = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<SongLog {self.title} by {self.artist}>'

@app.route('/')
def home():
    return render_template('MusicBxd.html')

@app.route('/spotify-login')
def spotify_login():
    auth_url = sp_oauth.get_authorize_url()
    flash('Successfully Logged In!', 'success')
    return redirect(auth_url)

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM login WHERE email = %s AND password = %s", (email, password))
    user = cur.fetchone()
    cur.close()

    if user:
        session['username'] = user[1]
        session['email'] = email
        flash('Logged in successfully!', 'success')
        return redirect(url_for('homepage'))
    else:
        return render_template('MusicBxd.html', error="Invalid username or password")

@app.route('/loginwithSpotify', methods=['POST'])
def loginSpoty():
    if sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    return redirect(url_for('homepage'))


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO login (username, email, password) VALUES (%s, %s, %s)",
                (username, email, password))
    mysql.connection.commit()
    cur.close()


    flash('Successfully registered!', 'success')
    return redirect(url_for('musicbxd'))

def get_email_by_username(username):
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM login WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    return user[0] if user else None

@app.route('/log-song', methods=['POST'])
def log_song():
    if 'username' not in session:
        return redirect(url_for('musicbxd'))

    artist = request.form.get('artist')
    title = request.form.get('title')
    comment = request.form.get('comment')

    rating = request.form.get('rate')
    for i in range(1, 6):
        if request.form.get(f'rate-{i}'):
            rating = i
            break

    user_email = session.get('email')

    if not user_email:
        return render_template('MusicBxd.html', error="User email not found. Please log in again.")

    if artist and title:
        new_log = SongLog(
            artist=artist,
            title=title,
            comment=comment,
            rating=rating,
            user_email=user_email
        )
        db.session.add(new_log)
        db.session.commit()
        print("Saved new song:", new_log)
        flash('Successfully Logged!', 'success')
        return redirect(url_for('homepage'))

    return redirect(url_for('homepage'))

@app.route('/logs')
def user_logs():
    if 'email' not in session:
        return redirect(url_for('musicbxd'))

    user_email = session['email']

    logs = SongLog.query.filter_by(user_email=user_email).all()

    return render_template('view.html', logs=logs)

@app.route('/Musicbxd')
def musicbxd():
    return render_template('MusicBxd.html')

from spotipy import Spotify

@app.route('/callback')
def callback():
    try:
        token_info = sp_oauth.get_access_token(request.args['code'])
        access_token = token_info['access_token']
        sp = Spotify(auth=access_token)

        user_info = sp.current_user()
        spotify_id = user_info['id']
        display_name = user_info.get('display_name', '')
        email = user_info.get('email')

        print("Spotify User Info:", user_info)

        if not email:
            return render_template('MusicBxd.html', error="Spotify account does not have an email.")

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM login WHERE email = %s", (email,))
        user = cur.fetchone()

        if user:
            cur.execute(
                "UPDATE login SET spotify_id = %s, spotify_display_name = %s WHERE email = %s",
                (spotify_id, display_name, email)
            )
        else:
            cur.execute(
                "INSERT INTO login (username, email, password, spotify_id, spotify_display_name) VALUES (%s, %s, %s, %s, %s)",
                (display_name, email, '', spotify_id, display_name)
            )

        mysql.connection.commit()
        cur.close()

        session['username'] = display_name
        session['email'] = email

        print("Login successful, redirecting to homepage.")
        flash('Welcome To MusicBxd', 'success')
        return redirect(url_for('homepage'))

    except Exception as e:
        print("Spotify callback error:", str(e))
        return render_template('MusicBxd.html', error="An error occurred during Spotify login.")


@app.route('/homepage')
def homepage():
    return render_template('Homepage.html')

@app.route('/recommendation')
def recommendation():
    return render_template('Recommendation.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('musicbxd'))


@app.route('/recommend-random')
def recommend_random():
    import random, requests

    LASTFM_API_KEY = '04ad112619f7064b2815e5d571a107d8'
    url = f"http://ws.audioscrobbler.com/2.0/?method=chart.gettoptracks&api_key={LASTFM_API_KEY}&format=json&limit=100"

    try:
        response = requests.get(url)
        tracks = response.json()['tracks']['track']
        random_track = random.choice(tracks)

        return {
            'title': random_track['name'],
            'artist': random_track['artist']['name'],
            'url': random_track['url']
        }

    except Exception as e:
        return {'error': 'Failed to fetch song.'}, 500

class LikedSong(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<LikedSong {self.title} by {self.artist}>'


@app.route('/Profile')
def profile():
    if 'email' not in session:
        return redirect(url_for('musicbxd'))

    user_email = session['email']
    liked_songs = LikedSong.query.filter_by(user_email=user_email).all()

    return render_template('Profile.html', liked_songs=liked_songs)


@app.route('/like-song', methods=['POST'])
def like_song():
    if 'email' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    title = request.form.get('title')
    artist = request.form.get('artist')

    if not title or not artist:
        return jsonify({'error': 'Invalid data'}), 400

    user_email = session.get('email')

    like = LikedSong(title=title, artist=artist, user_email=user_email)
    db.session.add(like)
    db.session.commit()

    return jsonify({'message': 'Song liked!'})

@app.route('/delete-log/<int:log_id>', methods=['DELETE'])
def delete_log(log_id):
    log = db.session.get(SongLog, log_id)
    if log:
        db.session.delete(log)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Log not found"}), 404

@app.route('/remove-like/<int:song_id>', methods=['POST'])
def remove_like(song_id):
    song = LikedSong.query.get_or_404(song_id)
    db.session.delete(song)
    db.session.commit()
    return redirect(url_for('profile'))


if __name__ == '__main__':
    app.run(debug=True)
