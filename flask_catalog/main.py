import os
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
import logging

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


CLIENT_ID=json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
app = Flask(__name__)

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from models import Base, User, Category, Item

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# provide a user registration and authentication system
# third-party OAuth authentication.
@app.route('/login')
def login():
    """
    create secret for auth.
    
    """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) 
          for x in xrange(32))
    login_session['state'] = state
    #"The current session state is %s" % login_session['state']
    
    return render_template('login.html', 
    STATE=state, login_session=login_session)
    

@app.route('/gconnect', methods=['POST'])
def gconnect():
    """
    oauth2 auth by email
    setup login_session
    """    
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
        response = make_response(
        json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    #login_session['credentials'] = credentials
    login_session['access_token'] = credentials.access_token 
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
    return redirect(url_for('showCategory', login_session=login_session))


# User Helper Functions


def createUser(login_session):
    """
    create user by login_session
    :login_session: information about the new user
    reutrn user id
    """
    newUser = User(name=login_session['username'], 
    email=login_session['email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """
    get user object by email
    :user_id: id of that user
    reutrn user object
    """
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """
    get user id by email
    :email: email of that user
    reutrn user id
    """
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None
        
@app.route('/gdisconnect')
def gdisconnect():
    """
    logout
    revoke the oauth2 token
    """
    access_token = login_session['access_token']
    
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: ' 
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
          % login_session['access_token']
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
        response = make_response(
          json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response    
        
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', login_session=login_session), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', login_session=login_session), 500

@app.route('/')
@app.route('/catalog')
def showCategory():
    """
    show main page

    render pages show all the categoryp
    """
    if request.method == 'GET':
        cats = session.query(Category).order_by(asc(Category.name))
        items = session.query(Item).order_by(desc(Item.id))
        return render_template('index.html', 
        cats=cats, latest=items, login_session=login_session)
    
    
@app.route('/catalog/<category>/items')
def showItem(category):     
    """
    show item in the category
    :category: category name 
    render a page with item for that category
    """   
    cats = session.query(Category).order_by(asc(Category.name))
    theid=session.query(Category).filter_by(name=category).one()
    its = session.query(Item).filter_by(category_id = theid.id).all()
    return render_template('index.html', 
    cats=cats, category=category, items=its, login_session=login_session)
      
@app.route('/catalog/<category>/<item>')
def descItem(category, item):
    """
    show the item description
    :category: category of the items
    :item: name of the items
    show the page with item description
    """
    #print "show item description"  + category + item
    it=session.query(Item).filter_by(name=item).one()
    return render_template('item.html', item=it, login_session=login_session)
    
#logged in

def login_check():
    """
    Registered users will have the ability to post, edit and delete their own items.
    """
    if 'username' not in login_session:
        return redirect('/login')

def owner_check(item):
    """
    Create, delete and update operations do consider authorization status prior to execution.
    :item: item to check for authorization
    if not owner it redirect to main page
    """
    if login_session['user_id'] != item.user_id:
        flash('Not the owner of item - cannot CRUD')
        return redirect(url_for('showCategory', login_session=login_session))
    
@app.route('/catalog/add', methods = ['GET','POST'])
def addItem():
    """
    add a new item for the category form input form
    redirect to show the item information
    """
    login_check()
    cats = session.query(Category).order_by(asc(Category.name))
    if request.method == 'POST':
        newItem = Item(name=request.form['name'], 
        description = request.form['description'], 
        user_id=login_session['user_id'], 
        category_id=int(request.form['category_id']))
        session.add(newItem)
        session.commit()
        flash('Item Successfully Added')
        return redirect(url_for('showItem', 
        category=newItem.category.name, login_session=login_session))
    else:
        return render_template('addItem.html', 
          cats=cats, login_session=login_session)
      
@app.route('/catalog/<item>/edit/<int:item_id>', methods = ['GET','POST'])
def editItem(item, item_id):
    """
    edit the items
    :item: name of the item to deleter
    :item_id: id of the item for editing
    :output: item updated and show that item's catalog
    """
    login_check()
    item = session.query(Item).filter_by(id = item_id).first()
    owner_check(item)
    
    cats = session.query(Category).order_by(asc(Category.name))
    if request.method == 'GET':
        return render_template('editItem.html', 
          item=item, cats=cats, login_session=login_session)   
    else:
        item.name=request.form['name']
        item.description=request.form['description']
        item.category_id=int(request.form['category_id'])
        session.add(item)
        session.commit()
        flash('Item Successfully Edited')
        return redirect(url_for('showCategory'))
      
    
@app.route('/catalog/<item>/delete', methods = ['GET','POST'])
def deleteItem(item):
    """
    delete the items
    :item: name of the item to delete
    :output: redirect to that item's category pages
    """
    login_check()
    item = session.query(Item).filter_by(name = item).first()
    owner_check(item)
    
    if request.method == 'GET': #CONFIRM MSG
        return render_template('deleteItem.html', 
          item=item, login_session=login_session)
    else: #delete for real
        cat=item.category.name
        session.delete(item)
        session.commit()
        flash('Item Successfully Deleted')
        return redirect(url_for('showItem', category=cat))

    
@app.route('/catalog.json')
def catalog():
    """
    The project implements a JSON endpoint that serves the same information as displayed in the HTML endpoints for an arbitrary item in the catalog.
    :output: json representation of all catalog
    """    
    catalogs = session.query(Category).order_by(asc(Category.name))
    return jsonify(Category=[ c.serialize for c in catalogs ])

    
if __name__ == '__main__':  
    console = logging.StreamHandler()
    log = logging.getLogger("asdasd")
    log.addHandler(console)
    log.setLevel(logging.DEBUG)
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
    
        