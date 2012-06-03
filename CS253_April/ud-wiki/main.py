import re
import os
import webapp2
import jinja2
import hashlib

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja_env = jinja2.Environment( loader = jinja2.FileSystemLoader(template_dir), autoescape=False)

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

class Users(db.Model):
    username = db.StringProperty(required = True)
    password = db.StringProperty(required = True)
    email = db.StringProperty(required = False)
    created = db.DateTimeProperty( auto_now_add = True)

class WikiPost(db.Model):
    name = db.StringProperty(required = False)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

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
            hashP = hashlib.md5(passw).hexdigest()
            us = Users( username = username, password = hashP , email = email)
            us.put()
            i = us.key().id()
            self.response.headers.add_header("Set-Cookie","user_id=" + str(i) + "|" + hashP +";Path=/")
            self.redirect("/")

class Login(Handler):
    def get(self):
        self.render("login.html")
        
    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        bp = db.GqlQuery("SELECT * FROM Users Where username='" + username + "' AND password='" + hashlib.md5(password).hexdigest()+"'" )
        if bp.count() > 0:
            self.response.headers.add_header("Set-Cookie","user_id=" + str(bp[0].username) + "|" + str(bp[0].password) +";Path=/")
            self.redirect("/");
        pass

class Logout(Handler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
        self.redirect("/login")

class EditPage(Handler):
    def get(self,lin):
        bp = db.GqlQuery("SELECT * FROM WikiPost Where name='"+lin[1:]+"'" )
        if bp.count() == 0:
            self.render("edit.html")
        else:
            self.render("edit.html",content = bp[0].content)

    def post(self,lin):
        content = self.request.get("content")
        WikiPost( name=lin[1:], content=content).put()
        self.redirect("/"+lin[1:])
        
class WikiPage(Handler):
    def get(self,lin):
        version = self.request.get("v")
        if version:
            enlace = lin[1:]
            bp = db.GqlQuery("SELECT * FROM WikiPost Where name='"+enlace+"'" )
            if bp.count() > 0:
                self.render("wikipage.html",content=bp[int(version)].content,place=enlace)
            else:
                self.redirect("/_edit/"+enlace)            
        else:
            bp = db.GqlQuery("SELECT * FROM WikiPost Where name='"+lin[1:]+"'" )
            if bp.count() > 0:
                self.render("wikipage.html",content=bp[bp.count()-1].content,place=lin[1:])
            else:
                self.redirect("/_edit/"+lin[1:])

class History(Handler):
    def get(self,lin):
        pages = db.GqlQuery("SELECT * FROM WikiPost Where name='"+lin[1:]+"'" )
        self.render("history.html",pages=pages, i = 1)

PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'
app = webapp2.WSGIApplication([('/signup', Signup),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/_edit' + PAGE_RE, EditPage),
                               ('/_history' + PAGE_RE, History ),
                               (PAGE_RE, WikiPage),
                               ],debug=True)
