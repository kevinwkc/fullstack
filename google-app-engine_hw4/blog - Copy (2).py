import os
import re
import random
import hashlib
import hmac
from string import letters

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

secret = '15648ksajfd$@#$'

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and self.user_obj=User.by_id(int(uid))
        
    def getPost(self):
        post_id = self.request.get('id')
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)  
        return post    
        
    def getComment(self):
        comment_id = self.request.get('id')
        key = db.Key.from_path('Comment', int(comment_id), parent=blog_key())
        comment = db.get(key)  
        return comment     

    def blogError(self, error):
        posts = greetings = Post.all().order('-created')
        self.render('front.html', posts = posts, error=error)           

def render_post(response, post):
    response.out.write('<b>' + post.subject + '</b><br>')
    response.out.write(post.content)

class MainPage(BlogHandler):
  def get(self):
      self.write('Hello, Udacity!')


##### user stuff
def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h) #h store in db

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt) #compare with db h

def users_key(group = 'default'):
    return db.Key.from_path('users', group)

class User(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True) #we dont store pw in db, just hash
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email) #create user but not store it yet

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u


##### blog stuff https://review.udacity.com/#!/rubrics/150/view

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Comment(db.Model):
    user=db.StringProperty(required = True)
    post_id = db.IntegerProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    
    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("comment.html", c = self)     

        
class Post(db.Model):
    user=db.StringProperty(required = True)
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    like=db.StringListProperty()
    unlike=db.StringListProperty()
    
    def getComments(self, post_id):
        return Comment.all().filter('post_id =', post_id)
        
    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self, like_cnt=len(self.like), unlike_cnt=len(self.unlike), comments=self.getComments(self.key().id()))

   

class NewComment(BlogHandler):
    def get(self):
        if self.user_obj:
            self.render("newcomment.html", post_id=self.request.get('id'))
        else:
            self.redirect("/login")

    def post(self):
        if not self.user:
            self.redirect('/login')
        
        user = self.user.name

        content = self.request.get('content')
        post_id = self.request.get('id')
        if  content:
            p = Comment(parent = blog_key(), user=user, content = content, post_id=int(post_id))
            p.put()     
            self.redirect('/blog')
            #self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "content, please!"
            self.render("newcomment.html",  content=content, error=error) 
            
class BlogFront(BlogHandler):
    def get(self):
        posts = greetings = Post.all().order('-created')
        self.render('front.html', posts = posts)

class LikePage(BlogHandler):
    def get(self):
        if not self.user:
            self.redirect('/login')    
        posts = greetings = Post.all().order('-created')
        self.render('front.html', posts = posts)
    def post(self):
        if not self.user:
            self.redirect('/login')
            
        p=self.getPost()
        
        if self.user.name != p.user and self.user.name not in p.like:
          p.like.append(self.user.name)
          p.put()
          self.redirect('/blog')
        else:
          self.blogError(error='cannot like the post')   

class UnLikePage(BlogHandler):
    def get(self):
        if not self.user:
            self.redirect('/login')    
        posts = greetings = Post.all().order('-created')
        self.render('front.html', posts = posts)
    def post(self):
        if not self.user:
            self.redirect('/login')
        p=self.getPost()
        if self.user.name != p.user and self.user.name not in p.unlike:
            p.unlike.append(self.user.name)
            p.put()
            self.redirect('/blog')
        else:
            self.blogError(error='cannot unlike the post')     

     
          
        
class PostPage(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        self.render("permalink.html", post = post)

class NewPost(BlogHandler):
    def get(self):
        if self.user:
            self.render("newpost.html")
        else:
            self.redirect("/login")

    def post(self):
        if not self.user:
            self.redirect('/login')
        
        user = self.user.name
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post(parent = blog_key(), user=user, subject = subject, content = content, like=[], unlike=[])
            p.put()         
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content, error=error)

            

class EditPost(BlogHandler):
        
    def get(self):
        if not self.user:
            self.redirect("/login")

        p=self.getPost()
        
        if self.user.name == p.user:
            self.render('editpost.html', p=p)
        else:
            self.blogError(error='post can only update by creator')

    def post(self):
        if not self.user:
            self.redirect('/login')
        
        p=self.getPost()
        p.subject = self.request.get('subject')
        p.content=self.request.get('content')
        if self.user.name == p.user:  
            p.put()
            self.render('editpost.html', p=p)
        else:
            self.blogError(error='post can only update by creator')
            #self.render('editpost.html', error=)  
            
           

class EditComment(BlogHandler):
        
    def get(self):
        if not self.user:
            self.redirect("/login")

        p=self.getComment()
        
        if self.user.name == p.user:
            self.render('editcomment.html', p=p)
        else:
            self.blogError(error='post can only update by creator')

    def post(self):
        if not self.user:
            self.redirect('/login')
        
        p=self.getComment()
        p.content=self.request.get('content')
        if self.user.name == p.user:  
            p.put()
            self.render('editcomment.html', p=p)
        else:
            self.blogError(error='post can only update by creator')
            #self.render('editpost.html', error=)              
            
class DeletePost(BlogHandler):
    def get(self):
        if self.user:
            self.redirect("/blog") #self.render("delpost.html")
        else:
            self.redirect("/login")

    def post(self):
        if not self.user:
            self.redirect('/login')
        
        post=self.getPost()
        
        if self.user.name == post.user:
            #delete for datastore
            post.delete()
              
            self.redirect('/blog') #self.redirect('/blog/%s' % str(p.key().id()))
        else:
            #error = "only owner can delete the post, please!"
            #self.redirect('/blog')
            self.blogError(error='post can only delete by creator')
            #self.render("newpost.html", subject=subject, content=content, error=error)

class DeleteComment(BlogHandler):
    def get(self):
        if self.user:
            self.redirect("/blog") #self.render("delpost.html")
        else:
            self.redirect("/login")

    def post(self):
        if not self.user:
            self.redirect('/login')
        
        comment=self.getComment()
        
        if self.user.name == comment.user:
            #delete for datastore
            comment.delete()
              
            self.redirect('/blog') #self.redirect('/blog/%s' % str(p.key().id()))
        else:
            #error = "only owner can delete the post, please!"
            #self.redirect('/blog')
            self.blogError(error='post can only delete by creator')
            #self.render("newpost.html", subject=subject, content=content, error=error)   
            
###### Unit 2 HW's
class Rot13(BlogHandler):
    def get(self):
        self.render('rot13-form.html')

    def post(self):
        rot13 = ''
        text = self.request.get('text')
        if text:
            rot13 = text.encode('rot13')

        self.render('rot13-form.html', text = rot13)


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

class Signup(BlogHandler):
    def get(self):
        self.render("signup-form.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username = self.username,
                      email = self.email)

        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError

class Unit2Signup(Signup):
    def done(self):
        self.redirect('/unit2/welcome?username=' + self.username)

class Register(Signup):
    def done(self):
        #make sure the user doesn't already exist
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username = msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/blog')

class Login(BlogHandler):
    def get(self):
        self.render('login-form.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/blog')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error = msg)

class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/blog')

class Unit3Welcome(BlogHandler):
    def get(self):
        if self.user:
            self.render('welcome.html', username = self.user.name)
        else:
            self.redirect('/signup')

class Welcome(BlogHandler):
    def get(self):
        username = self.request.get('username')
        if valid_username(username):
            self.render('welcome.html', username = username)
        else:
            self.redirect('/unit2/signup')

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/unit2/rot13', Rot13),
                               ('/unit2/signup', Unit2Signup),
                               ('/unit2/welcome', Welcome),
                               ('/blog/?', BlogFront),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/newpost', NewPost),
                               ('/blog/delpost', DeletePost),
                               ('/blog/editpost', EditPost),                            
                               ('/blog/newcomment', NewComment),
                               ('/blog/editcomment', EditComment),
                               ('/blog/delcomment', DeleteComment), 
                               ('/blog/likepost', LikePage),                              
                               ('/blog/unlikepost', UnLikePage),                               
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/unit3/welcome', Unit3Welcome),
                               ],
                              debug=True)
