import webapp2
import jinja2
import logging
from models.comment import Comment
from models.post import Post
from models.user import User
from helper import *

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
        delattr(self, "user")

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

    def getName(self):
        logging.info(self.user)
        if not self.user:
            self.redirect('/login')
        else:
            return self.user.name

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
        self.render('front.html', posts=posts, error=error)





class MainPage(BlogHandler):

    def get(self):
        self.write('Hello, Udacity!')


# blog stuff https://review.udacity.com/#!/rubrics/150/view




class NewComment(BlogHandler):

    def get(self):
        if self.user:
            self.render("newcomment.html", post_id=self.request.get('id'))
        else:
            self.redirect("/login")

    def post(self):
        if not self.user:
            self.redirect('/login')

        name = self.getName()

        content = self.request.get('content')
        post_id = self.request.get('id')
        if content:
            p = Comment(
                parent=blog_key(), user=name,
                content=content, post_id=int(post_id))
            p.put()
            self.redirect('/blog/comment/%s' % str(p.key().id()))
        else:
            error = "content, please!"
            self.render("newcomment.html",  content=content, error=error)


class CommentPage(BlogHandler):

    def get(self, comment_id):
        key = db.Key.from_path('Comment', int(comment_id), parent=blog_key())
        comment = db.get(key)

        if not comment:
            self.error(404)
            return

        self.render("c_permalink.html", comment=comment)


class BlogFront(BlogHandler):

    def get(self):
        posts = greetings = Post.all().order('-created')
        self.render('front.html', posts=posts)


class LikePost(BlogHandler):

    def get(self):
        if not self.user:
            self.redirect('/login')
        posts = greetings = Post.all().order('-created')
        self.render('front.html', posts=posts)

    def post(self):
        if not self.user:
            self.redirect('/login')

        name = str(self.getName())
        p = self.getPost()

        if name != 'None' and name != p.user and name not in p.like:
            p.like.append(name)
            p.put()
            self.redirect('/blog')
        else:
            self.blogError(error='cannot like the post')


class UnLikePost(BlogHandler):

    def get(self):
        if not self.user:
            self.redirect('/login')
        posts = greetings = Post.all().order('-created')
        self.render('front.html', posts=posts)

    def post(self):
        if not self.user:
            self.redirect('/login')

        name = str(self.getName())

        p = self.getPost()

        if name != 'None' and name != p.user and name not in p.unlike:
            p.unlike.append(name)
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

        self.render("permalink.html", post=post)


class NewPost(BlogHandler):

    def get(self):
        if self.user:
            self.render("newpost.html")
        else:
            self.redirect("/login")

    def post(self):
        if not self.user:
            self.redirect('/login')

        user = self.getName()
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post(parent=blog_key(), user=user, subject=subject,
                     content=content, like=[], unlike=[])
            p.put()
            self.redirect('/blog/post/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render(
                "newpost.html", subject=subject, content=content, error=error)


class EditPost(BlogHandler):

    def get(self):

        if not self.user:
            self.redirect("/login")
        post_id = self.request.get('id')
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        p = db.get(key)
        # p=self.getPost()
        name = self.getName()
        if name == p.user:
            self.render('editpost.html', p=p)
        else:
            self.blogError(error='post can only update by creator')

    def post(self):
        if not self.user:
            self.redirect('/login')

        p = self.getPost()
        p.subject = self.request.get('subject')
        p.content = self.request.get('content')
        name = self.getName()
        if name == p.user:
            p.put()
            self.render('editpost.html', p=p)
        else:
            self.blogError(error='post can only update by creator')
            # self.render('editpost.html', error=)


class EditComment(BlogHandler):

    def get(self):
        if not self.user:
            self.redirect("/login")

        p = self.getComment()
        name = self.getName()
        if name == p.user:
            self.render('editcomment.html', p=p)
        else:
            self.blogError(error='post can only update by creator')

    def post(self):
        if not self.user:
            self.redirect('/login')

        p = self.getComment()
        p.content = self.request.get('content')
        name = self.getName()
        if name == p.user:
            p.put()
            self.render('editcomment.html', p=p)
        else:
            self.blogError(error='post can only update by creator')
            # self.render('editpost.html', error=)


class DeletePost(BlogHandler):

    def get(self):
        if self.user:
            self.redirect("/blog")  # self.render("delpost.html")
        else:
            self.redirect("/login")

    def post(self):
        if not self.user:
            self.redirect('/login')

        post = self.getPost()

        name = self.getName()
        if name == post.user:
            # delete for datastore
            for c in post.getComments():
                c.delete()
            post.delete()

            # self.redirect('/blog/%s' % str(p.key().id()))
            self.redirect('/blog')
        else:
            # error = "only owner can delete the post, please!"
            # self.redirect('/blog')
            self.blogError(error='post can only delete by creator')
            # self.render("newpost.html", subject=subject, content=content, error=error)


class DeleteComment(BlogHandler):

    def get(self):
        if self.user:
            self.redirect("/blog")  # self.render("delpost.html")
        else:
            self.redirect("/login")

    def post(self):
        if not self.user:
            self.redirect('/login')

        comment = self.getComment()
        name = self.getName()
        if name == comment.user:
            # delete for datastore
            comment.delete()

            # self.redirect('/blog/%s' % str(p.key().id()))
            self.redirect('/blog')
        else:
            # error = "only owner can delete the post, please!"
            # self.redirect('/blog')
            self.blogError(error='post can only delete by creator')
            # self.render("newpost.html", subject=subject, content=content, error=error)

# Unit 2 HW's


class Rot13(BlogHandler):

    def get(self):
        self.render('rot13-form.html')

    def post(self):
        rot13 = ''
        text = self.request.get('text')
        if text:
            rot13 = text.encode('rot13')

        self.render('rot13-form.html', text=rot13)





class Signup(BlogHandler):

    def get(self):
        self.render("signup-form.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username=self.username,
                      email=self.email)

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
        # make sure the user doesn't already exist
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username=msg)
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
            self.render('login-form.html', error=msg)


class Logout(BlogHandler):

    def get(self):
        self.logout()
        self.redirect('/blog')


class Unit3Welcome(BlogHandler):

    def get(self):
        if self.user:
            name = self.getName()
            self.render('welcome.html', username=name)
        else:
            self.redirect('/signup')


class Welcome(BlogHandler):

    def get(self):
        username = self.request.get('username')
        if valid_username(username):
            self.render('welcome.html', username=username)
        else:
            self.redirect('/unit2/signup')