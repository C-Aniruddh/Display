from flask import Flask, render_template, url_for, request, session, redirect, jsonify, json
from flask_imgur import Imgur
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson import json_util
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
            y = x + 1
            z = str(y)
            img_find=wallpaper.find_one({'image_id' : z})
            img_url = img_find['imgur_link']
            imgur_link.append(img_url)
            img_auth = img_find['author']
            image_author.append(img_auth)
            img_titl = img_find['title']
            image_title.append(img_titl)

        return render_template('home.html', image_author=image_author, image_title=image_title, imgur_link=imgur_link, imagenumber=imagelist)

    return render_template('index.html')

@app.route('/myuploads')
def myuploads():
    if 'username' in session:
        uploader = session['username']
        wallpaper = mongo.db.wallpaper
        find_image = wallpaper.find({'uploadedby' : uploader})
        count = find_image.count()
        imagelist = range(0, count, 1)
        imgur_link = []
        image_author = []
        image_title = []

        for x in imagelist:
            y = x + 1
            z = str(y)
            img_find=wallpaper.find_one({'uploader_count' : z, 'uploadedby' : uploader})
            img_url = img_find['imgur_link']
            imgur_link.append(img_url)
            img_auth = img_find['author']
            image_author.append(img_auth)
            img_titl = img_find['title']
            image_title.append(img_titl)

        return render_template('myuploads.html', image_author=image_author, image_title=image_title, imgur_link=imgur_link, imagenumber=imagelist)
    return 'you have to be logged in'

@app.route('/search/<searchq>')
def search(searchq):
    if 'username' in session:
        query = searchq
        wallpaper = mongo.db.wallpaper
        find_img = wallpaper.find({'image_tags':{"$regex": query}})
        count = find_img.count()
        print count
        imagelist = range(0, count, 1)
        imgur_link = [img_url for img_url in imagelist]
        image_author = [img_auth for img_auth in imagelist]
        image_title = [img_titl for img_titl in imagelist]
        print imgur_link
        for img_url in imagelist:
            img_find = wallpaper.find_one({'image_tags':{"$regex": query}})
            img_url = img_find['imgur_link']
            imgur_link.append(img_url)
        for img_auth in imagelist:
            img_find = wallpaper.find_one({'image_tags': {"$regex": query}})
            img_auth = img_find['author']
            image_author.append(img_auth)
        for img_titl in imagelist:
            img_find = wallpaper.find_one({'image_tags': {"$regex": query}})
            img_titl = img_find['title']
            image_title.append(img_titl)

        return render_template('search.html', image_author=image_author, image_title=image_title,
                               imgur_link=imgur_link, imagenumber=imagelist)

    return 'you have to be logged in'

@app.route('/material')
def material():
    return render_template('material.html')

@app.route('/image/<img_id>')
def image(img_id):
    if 'username' in session:
        wallpaper = mongo.db.wallpaper
        x = str(img_id)
        img_find = wallpaper.find_one({'image_id' : x})
        imgur_link = img_find['imgur_link']
        image_author = img_find['author']
        image_title = img_find['title']
        return render_template('image.html', image_title=image_title, image_author=image_author, imgur_link=imgur_link)
    return 'HA'


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
        image_tag = request.form['image_tags']
        uploader = session['username']
        uploader_find = wallpaper.find({'uploadedby' : uploader})
        uploader_count = uploader_find.count() + 1
        image_author = request.form['image_author']
        image_title = request.form['image_title']
        image_uploaddate = timestamp.strftime("%Y-%m-%d")
        wallpaper.insert({'uploadedby' : uploader, 'uploader_count': str(uploader_count), 'image_tags' : image_tag, 'image_id': str(image_id), 'type': 'image', 'title': image_title, 'author': image_author, 'imgur_link': image_data["data"]["link"], 'image_uploaddate' : image_uploaddate})
    return render_template('submit2.html')

@app.route('/get', methods=['POST', 'GET'])
def get():
    wallpaper = mongo.db.wallpaper
    result = wallpaper.find()
    return str(json.dumps({'results' : list(result)}, default = json_util.default, indent = 4))

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True, host ='0.0.0.0',port=5000)