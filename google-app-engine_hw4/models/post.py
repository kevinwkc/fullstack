from google.appengine.ext import db
     
class Post(db.Model):
    user=db.StringProperty(required = True)
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    like=db.StringListProperty()
    unlike=db.StringListProperty()
    
    def getComments(self):
        return Comment.all().filter('post_id =', self.key().id()).order('-created')
        
    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self, like_cnt=len(self.like), unlike_cnt=len(self.unlike), comments=self.getComments())