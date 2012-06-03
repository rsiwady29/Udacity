import re
import os
import webapp2
import jinja2
import hashlib
import json

from datetime import datetime, timedelta
from google.appengine.ext import db
from google.appengine.api import memcache

template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja_env = jinja2.Environment( loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

class Handler(webapp2.RequestHandler):
    def write( self, *a, **kw):
        self.response.out.write(*a,**kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render( self, template, **kw):
        self.write(self.render_str(template,**kw))

    def render_json(self, d):
        jsont = json.dumps(d)
        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        self.write(jsont)

class BlogPost(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

    def as_dict(self):
        dictio = { 'subject': self.subject,
                   'content' : self.content,
                   'created' : self.created.strftime('%c')
                }
        return dictio
    

class Users(db.Model):
    username = db.StringProperty(required = True)
    password = db.StringProperty(required = True)
    email = db.StringProperty(required = False)
    created = db.DateTimeProperty( auto_now_add = True)

    @classmethod
    def by_name(cls, name):
        u = Users.all().filter('name =', name).get()
        return u

def age_set(key,val):
    save_time = datetime.utcnow()
    memcache.set(key, (val, save_time))

def age_get(key):
    r = memcache.get(key)
    if r:
        val, save_time = r
        age = (datetime.utcnow() - save_time).total_seconds()
    else:
        val, age = None,0
    return val,age

def get_posts( update = False ):
    q = BlogPost.all().order('-created').fetch(limit=10)
    mc_key = 'BLOGS'
    posts, age = age_get(mc_key)
    if update or posts is None:
        posts = list(q)
        age_set(mc_key,posts)
    return posts,age

def age_str(age):
    s = 'queried %s seconds ago'
    age = int(age)
    if age==1:
        s = s.replace('seconds', 'second')
    return s % age

class Blog(Handler):
    def render_index(self, subject="", content="", error=""):
        #bp = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC")
        posts, age = get_posts()
        if self.request.url.endswith('.json'):
            self.render_json([p.as_dict() for p in bp])
        else:
            self.render("blog.html", subject = subject, content=content, error=error, post = posts, age=age_str(age))
    
    def get(self):
        self.render_index()

    def post(self):
        pass

class NewPost(Handler):
    def get(self):
        self.render("newpost.html")
        
    def post(self):
        sub = self.request.get("subject")
        cont = self.request.get("content")

        if sub and cont:
            bp = BlogPost( subject = sub, content = cont)
            bp.put()
            i = bp.key().id()
            self.redirect("/blog/"+str(i))
        else:
            self.render("newpost.html", subject = sub ,
                        content=cont,error="Error")

class PermaLink(Handler):
    def get(self,perm):
        post_key = 'P_' + perm

        post,age = age_get(post_key)
        if not post:
            post = BlogPost.get_by_id(int(perm))
            age_set(post_key, post)
            age = 0

        if not post:
            self.error(404)
            return
        
        if self.request.url.endswith('.json'):
            self.render_json( bp.as_dict() )
        else:
            self.render("permalink.html", post = post, age = age_str(age))
        
    def post(self):
        pass

class Rot13(Handler):
    def get(self):
        self.render("rot.html")

    def post(self):
        rot = ""
        texto = self.request.get("text")
        if texto:
            rot = texto.encode('rot13')
        self.render('rot.html',text=rot)

class VisitCounter(Handler):
    def get(self):
        self.response.headers['Content-Type'] = "text/plain"
        visits = self.request.cookies.get("visits", "0" )

        if visits.isdigit():
            visits = int(visits) + 1
        else:
            visits = 0
        self.response.headers.add_header("Set-Cookie", "visits=%s" % visits)
        self.render("visit_count_cookies.html", visits = visits)
        
    def post(self):
        pass

class Signup(Handler):
    def get(self):
        self.render("signup.html")

    def post(self):
        username = self.request.get("username");
        passw = self.request.get("password");
        verify = self.request.get("verify");
        email = self.request.get("email");
        
        error = False

        if not valid_username(username):
            error = True

        if not valid_password(passw):
            error = True
        elif passw != verify:
            error = True

        if not valid_email(email):
            error = True

        if error:
            self.render("signup.html",error="Error")
        else:
            u = Users.by_name(username)
            if not u:
                hashP = hashlib.md5(passw).hexdigest()
                us = Users( username = username, password = hashP , email = email)
                us.put()
                i = us.key().id()
                self.response.headers.add_header("Set-Cookie","user_id=" + str(i) + "|" + hashP +";Path=/")
                self.redirect("/blog/welcome")
            else:
                self.render("signup.html",error="Error")

class Welcome(Handler):
    def get(self):
        user = self.request.cookies.get("user_id")
        if user:
            userid = user[:user.find("|")]
            us = Users.get_by_id(int(userid))
            if us:
                self.render("welcome.html",username=us.username)
            else:
                self.redirect("/blog/signup")
        else:
            self.redirect("/blog/signup")
            
    def post(self):
        user = self.request.cookies.get("user_id")
        userid = user[:user.find("|")]
        us = Users.get_by_id(int(userid))
        if us:
            self.render("welcome.html",username=us.username)
        else:
            self.redirect("/blog/signup")

class Login(Handler):
    def get(self):
        self.render("login.html")
    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        bp = db.GqlQuery("SELECT * FROM Users Where username='" + username + "' AND password='" + hashlib.md5(password).hexdigest()+"'" )
        if bp.count() > 0:
            self.response.headers.add_header("Set-Cookie","user_id=" + str(i) + "|" + str(bp[0].password) +";Path=/")
            self.redirect("/blog/welcome");
        else:
            self.render("login.html",error="error")

class Logout(Handler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
        self.redirect("/blog/signup")

class Flush(Handler):
    def get(self):
        memcache.flush_all()
        self.redirect("/blog")

    def post(self):
        memcache.flush_all()
        self.redirect("/blog")
        
app = webapp2.WSGIApplication([('/blog/?(?:.json)?', Blog),
                               ('/blog/newpost',NewPost),
                               ('/blog/(\d+)(?:.json)?',PermaLink),
                               ('/rot13',Rot13),
                               ('/visit_counter',VisitCounter),
                               ('/blog/signup',Signup),
                               ('/blog/welcome',Welcome),
                               ('/blog/login',Login),
                               ('/blog/logout',Logout),
                               ('/blog/flush',Flush)],
                              debug=True)






















