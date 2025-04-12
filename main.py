import os
from flask import Flask, request, redirect, session, url_for, render_template
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(64)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'login'

mysql = MySQL(app)


client_id = 'e277fd6395144b87a080712a4bfd11c2'
client_secret = '229559746a76424e97d05f6a7ad6f3f5'
redirect_uri = 'http://localhost:5000/callback'
scope = 'user-read-private'

cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True
)

@app.route('/Musicbxd')
def musicbxd():
    return render_template('MusicBxd.html')

@app.route('/')
def home():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    return redirect(url_for('homepage'))

@app.route('/callback')
def callback():
    sp_oauth.get_access_token(request.args['code'])
    return redirect(url_for('homepage'))


@app.route('/homepage')
def homepage():
    return render_template('Homepage.html')


@app.route('/View')
def view():
    return render_template('View.html')


@app.route('/Profile')
def profile():
    return render_template('Profile.html')


@app.route('/recommendation')
def recommendation():
    return render_template('Recommendation.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('musicbxd'))

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
        return redirect(url_for('homepage'))
    else:
        return render_template('MusicBxd.html', error="Invalid username or password")

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

    return redirect(url_for('musicbxd'))



if __name__ == '__main__':
    app.run(debug=True)

