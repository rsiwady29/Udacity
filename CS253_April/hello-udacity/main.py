#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by    applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import re


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$");
PASS_RE = re.compile(r"^.{3,20}$");
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$");

MainForm = """
<form action="/Rot13">
    <input type="submit" value="Rot13"/>
</form>
<form action="/Signup">
    <input type="submit" value="Signup"/>
</form>
"""

RotForm ="""
<h1>Enter some text to ROT13:</h1>
<form method="post">
    <textarea name="text">

    </textarea>
    <br>
    <input type="submit">
</form>
"""

SignupForm = """
<h1> Signup </h1>
<form method="post">
    <label> Username </label>
    <input type="text" name="username" required>
    <br>
    <label> Password </label>
    <input type="password" name="password" required>
    <br>
    <label> Verify Password </label> 
    <input type="password" name="verify" required>
    <br>
    <label> Email (optional) </label> 
    <input type="text" name="email">
    <br>
    <input type="submit">
</form>
"""

def valid_username(username):
    return username and USER_RE.match(username)

def valid_password(password):
    return password and PASS_RE.match(password)

def valid_email(email):
    return not email or EMAIL_RE.match(email)
        
class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(MainForm)

class Rot(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(RotForm)
    def post(self):
        texto = self.request.get("text")
        rot = rotear(texto)
        self.response.out.write(rot)

    def rotear(texto):
        rot = ""
        for letra in texto:
            r = ord(letra) + 13
            rot += chr( ord(letra) + 13 )
        return rot
            

class Signup(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(SignupForm);

    def post(self):
        username = self.request.get("username");
        passw = self.request.get("password");
        verify = self.request.get("verify");
        email = self.request.get("email");
        
        error = False
        
        #if PASS_RE.match(passw) and PASS_RE.match(verify) and USER_RE.match(us):
         #   if email:
          #      if not EMAIL_RE.match(email):
           #         error = True
            #if passw != verify:
             #   error = True
        #else:
         #   error = True

        if not valid_username(username):
            error = True

        if not valid_password(passw):
            error = True
        elif passw != verify:
            error = True

        if not valid_email(email):
            error = True

        if error:
            self.response.out.write(SignupForm)
        else:
            self.redirect("/welcome?username=" + username);        

class Welcome(webapp2.RequestHandler):
    def get(self):
        username = self.request.get("username")
        if username and USER_RE.match(username):
            msg = "<h1>Welcome, "
            msg += username
            msg += "!</h1>"
            self.response.out.write(msg);
        else:
            self.redirect("/Signup");

app = webapp2.WSGIApplication([('/',  MainHandler),
                               ('/Rot13', Rot),
                               ('/Signup', Signup),
                               ('/Welcome', Welcome)
                               ],
                              
                              debug=True)


























