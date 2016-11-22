from flask import Flask, render_template, url_for, request, session, redirect, jsonify
from flask_imgur import Imgur
from flask_pymongo import PyMongo
from bson.json_util import dumps
import bcrypt
import datetime

app = Flask(__name__)

timestamp = datetime.datetime.now()

app.config['MONGO_DBNAME'] = 'aniruddh'
app.config['MONGO_URI'] = 'mongodb://flaskmongo:flask@ds157187.mlab.com:57187/aniruddh'
app.config['IMGUR_ID'] = '7cd6cbeb3c61371'
mongo = PyMongo(app)
imgur_handler = Imgur(app)

@app.route('/')
def index():

    if 'username' in session:
        wallpaper = mongo.db.wallpaper
        count = wallpaper.count()
        imagelist = range(0, count, 1)
        user = session['username']
        imgur_link = []
        image_author = []
        image_title = []

        for x in imagelist:
            img_find=wallpaper.find_one({'image_id' : x+1})
            img_url = img_find['imgur_link']
            imgur_link.append(img_url)
            img_auth = img_find['author']
            image_author.append(img_auth)
            img_titl = img_find['title']
            image_title.append(img_titl)

        return render_template('home.html', image_author=image_author, image_title=image_title, imgur_link=imgur_link, imagenumber=imagelist)

    return render_template('index.html')

@app.route('/material')
def material():
    return render_template('material.html')

@app.route('/userlogin', methods=['POST','GET'])
def userlogin():
    if 'username' in session:
        return redirect('/home')

    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name' : request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
            session['username'] = request.form['username']
            return redirect(url_for('index'))

    return 'Invalid username/password combination'

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if 'username' in session:
        return "not allowed     "
    if request.method == 'POST':
        users = mongo.db.users
        user_fname = request.form['name']
        user_email = request.form['email']
        existing_user = users.find_one({'name' : request.form['username'], 'email' : user_email})
        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'fullname': user_fname, 'email': user_email, 'name' : request.form['username'], 'password' : hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        
        return 'A user with that Email id/username already exists'

    return render_template('register.html')

@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if request.method == 'POST':
        wallpaper = mongo.db.wallpaper
        image = request.files['uploaded_image']
        image_data = imgur_handler.send_image(image)
        image_id = wallpaper.count() + 1
        image_data["success"]
        image_data["data"]["height"]
        image_data["data"]["link"]
        image_data["data"]["deletehash"]

        image_author = request.form['image_author']
        image_title = request.form['image_title']
        image_uploaddate = timestamp.strftime("%Y-%m-%d")
        wallpaper.insert({'image_id': image_id, 'type': 'image', 'title': image_title, 'author': image_author, 'imgur_link': image_data["data"]["link"], 'image_uploaddate' : image_uploaddate})

    return render_template('submit2.html')

@app.route('/get', methods=['POST', 'GET'])
def get():
    wallpaper = mongo.db.wallpaper
    result = wallpaper.find()
    return dumps(result)

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True, port=5000)