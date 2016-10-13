
import webapp2
import jinja2
import logging
from handler import *

logging.getLogger().setLevel(logging.INFO)

# https://review.udacity.com/#!/rubrics/150/view

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/unit2/rot13', Rot13),
                               ('/unit2/signup', Unit2Signup),
                               ('/unit2/welcome', Welcome),
                               ('/blog/?', BlogFront),
                               ('/blog/post/([0-9]+)', PostPage),
                               ('/blog/comment/([0-9]+)', CommentPage),
                               ('/blog/newpost', NewPost),
                               ('/blog/delpost', DeletePost),
                               ('/blog/editpost', EditPost),
                               ('/blog/newcomment', NewComment),
                               ('/blog/editcomment', EditComment),
                               ('/blog/delcomment', DeleteComment),
                               ('/blog/likepost', LikePost),
                               ('/blog/unlikepost', UnLikePost),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/unit3/welcome', Unit3Welcome),
                               ],
                              debug=True)
