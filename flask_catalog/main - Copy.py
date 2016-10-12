import os
from flask import Flask, render_template, redirect, url_for, flash
'''
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# New imports for /login
from flask import session as login_session
import random
import string

# IMPORTS FOR gconnect
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

#https://classroom.udacity.com/nanodegrees/nd004/parts/0041345408/modules/348776022975462/lessons/3487760229239847/concepts/36269487530923#

basedir = os.path.abspath(os.path.dirname(__file__))

CLIENT_ID=json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret key'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'catalog.db')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

#manager = Manager(app)
bootstrap = Bootstrap(app)
#moment = Moment(app)
db = SQLAlchemy(app)

from . import models, forms

'''
https://developers.google.com/identity/protocols/OAuth2  
https://youtu.be/YLHyeSuBspI  
https://developers.google.com/oauthplayground/   

https://www.udacity.com/wiki/ud330/setup?_ga=1.65042476.309062196.1475106786 demo oauth

https://classroom.udacity.com/nanodegrees/nd004/parts/0041345408/modules/348776022975461/lessons/3967218625/concepts/39636486130923#
https://console.developers.google.com/apis


https://github.com/udacity/ud330/blob/master/Lesson2/step2/project.py

pip install werkzeug==0.8.3
pip install flask==0.9
pip install Flask-Login==0.1.3
Note: If you get a permissions error, you will need to include sudo at the beginning of each command. That should look like this: sudo pip install flask==0.9
'''
# provide a user registration and authentication system
# third-party OAuth authentication.
@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    #"The current session state is %s" % login_session['state']
    
    return render_template('login.html', STATE=state)
    
    '''
    form = LoginForm()
    #logic is wrong
    if form.validate_on_submit():
        old_username = session.get('username')
        if old_username is not None and old_username != form.username.data:
            flash('Looks like you have changed your username!')
        session['username'] = form.username.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, username=session.get('username'))
    '''

@app.route('/gconnect', methods=['POST'])
def gconnect():
    
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id=getUserID(login_session['email'])
    if not user_id:
      user_id = createUser(login_session)
    login_session['user_id']=user_id
    
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return redirect(url_for('showCategory'))


# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None
        
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: ' 
    print login_session['username']
    if access_token is None:
      print 'Access Token is None'
    	response = make_response(json.dumps('Current user not connected.'), 401)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
      del login_session['access_token'] 
    	del login_session['gplus_id']
    	del login_session['username']
    	del login_session['email']
    	del login_session['picture']
    	response = make_response(json.dumps('Successfully disconnected.'), 200)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    else:	
    	response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    	response.headers['Content-Type'] = 'application/json'
    	return response    
        
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/')
def showCategory():
    if request.method == 'GET':
      cats = Category.query.order_by(Category.name.desc()).all()
      items = Item.query.order_by(Item.id.desc()).all()
      return render_template('index.html', cats=cats, latest=items)
    
    
@app.route('/catalog/<category>/items')
def showItem(category):      
      items = Item.query.filter(Item.category.name == category).all()
      return render_template('index.html', category=category, items=items)
      
@app.route('/catalog/<category>/<item>')
def descItem(category, item):
    print "show item description"  + category + item
    item=Item.query.filter(Item.name=item).first()
    return render_template('item.html', item=item)
    
#logged in
'''
Registered users will have the ability to post, edit and delete their own items.
'''
def login_check():
    if 'username' not in login_session:
      return redirect('/login')

def owner_check():
    if login_session['user_id'] != request.form['id']:
      return flash('Not the owner of item - cannot CRUD')
    
@app.route('/catalog/add')
def addItem(item):
    login_check()
    
    if request.method == 'POST':
      print "add item" + item    
      newItem = Item(name=request.form['name'], description = request.form['description'], user_id=login_session['user_id'])
      db.session.add(newItem)
      db.session.commit()
      return redirect('/')
    else:
      return render_template('newItem.html')
      
@app.route('/catalog/<item>/edit', methods = ['GET','POST'])
def editItem(item):
    login_check()
    
    owner_check()
    if request.method == 'GET':
      print "update item" + item    
      
    
@app.route('/catalog/<item>/delete', methods = ['GET','POST'])
def deleteItem(item):
    login_check()
    
    owner_check()
    item = Item.query.filter(Item.name == item).first()
    if request.method == 'GET': #CONFIRM MSG
        return render_template('deleteItem.html', confirm=True, item=item)
    else: #delete for real
        db.session.delete(item)
        return redirect('/')
    
@app.route('/catalog.json')
def catalog():
    catalogs = db.session.query(Catalog).order_by(asc(Catalog.name))
    print catalogs.serialize() 

#https://www.lynda.com/Flask-tutorials/Implementing-Update/521200/533068-4.html    

    
if __name__ == '__main__':
    db.create_all()
    app.debug = True
    app.run(host='localhost', port=5000)
    
        