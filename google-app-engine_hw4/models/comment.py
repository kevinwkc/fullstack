from google.appengine.ext import db
from helper import *

class Comment(db.Model):
    user=db.StringProperty(required = True)
    post_id = db.IntegerProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    
    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("comment.html", c = self)     
