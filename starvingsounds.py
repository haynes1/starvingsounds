import os
import re
import random
import hashlib
import hmac
import urllib2
import json
import pdb
import logging
import random, string
from string import letters
import csv

import webapp2
import jinja2
import cgi
from google.appengine.ext.webapp.util import run_wsgi_app


from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.db import GqlQuery
from google.appengine.api import mail

#from oauth2client.client import flow_from_clientsecrets
#from oauth2client.client import FlowExchangeError
#import httplib2
#import requests


#logging.error('my string')

login_session = {}

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)
#---------------------------Input Validation Functions----------------------------
EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return email and EMAIL_RE.match(email)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

ZIP_RE = re.compile(r'^[0-9]{5}(?:-[0-9]{4})?$')
def valid_zip(zip):
    return zip and ZIP_RE.match(zip)

DISTRICT_RE = re.compile(r'^[A-Z]{2}[:]{1}[1-9]{1}')
def valid_district(district):
    return district and DISTRICT_RE.match(district)

#---------------------------User Implementation Functions--------------------------
def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(email, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(email + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def h_valid_pw(email, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(email, password, salt)


#--------------------------DB Classes----------------------------------------

class User(db.Model):
    username = db.StringProperty(required = True)
    email = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    district = db.StringProperty()
    age = db.IntegerProperty()
    gender = db.StringProperty()
    created = db.DateTimeProperty(required = True, auto_now = True)
    last_modified = db.DateTimeProperty(required = True, auto_now = True)
    token = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid)

    @classmethod
    def by_email(cls, email):
        u = cls.all().filter('email =', email).get()
        return u

    @classmethod
    def by_username(cls, username):
        u = cls.all().filter('username =', username).get()
        return u

    @classmethod
    def register(cls, username, email, pw):
        pw_hash = make_pw_hash(username, pw)
        return cls( username = username,
                    email = email,
                    pw_hash = pw_hash)

    @classmethod
    def login(cls, username, pw):
        u = cls.by_username(username)
        if u and valid_pw(username, pw, u.pw_hash):
            return u

class EmailSignee(db.Model):
    created = db.DateTimeProperty(required = True, auto_now = True)
    email = db.StringProperty(required = True)
    name = db.StringProperty(required = True)

    @classmethod
    def by_email(cls, email):
        u = cls.all().filter('email =', email).get()
        return u

#--------------------------Pages----------------------------------------
class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class Home(BaseHandler):

    def get(self):
        self.render('home.html')

    def post(self):
        self.render('home.html')

class Matchups(BaseHandler):
    matchup1 = '1;Griz,Fine Way To Die,11,2,18,3;Chemical Brothers,Galvanize,11,3,15,2'
    matchup2 = '1;Jungle,Busy Earning,11,1,17,3;Griz,Stop Trippin,12,1,18,3'
    matchup3 = '1;Kendrick Lamar,The Blacker The Berry,10,1,12,1;Jay Z,Justify My Thug,9,1,15,2'
    matchup4 = '2;Jungle,Time,10,2,17,3;Mark E Bassy,Relapse,8,2,10,3'
    
    def get(self):
        self.render('matchups.html')

    def post(self):
        funct = self.request.get('funct')
        current_set = self.request.get('current_set')
        response = self.matchup1
        if funct == 'getSet':
            next_set = (int(current_set) + 1) % 6
            if next_set == 2:
                response = self.matchup2
            if next_set == 3:
                response = self.matchup3
            if next_set == 4:
                response = self.matchup4
        self.response.out.write(response)

class Signup(BaseHandler):
    def get(self):
        self.render('signup.html')

    def post(self):
        self.render('signup.html')

class Profile(BaseHandler):
    def get(self):
        self.render('profile.html')

    def post(self):
        self.render('profile.html')

class Esf(BaseHandler):
    def get(self):
        self.render('esf.html')

    def post(self):
        msg = 'invalid email'
        name = self.request.get('name')
        email = self.request.get('email')
        if valid_email(email):
            msg = 'valid email'
            e = EmailSignee.by_email(email)
            if e:
                msg ='already on list'
                self.write(msg)
            else: #vetted email: add to db, send thankyou email, and success code to front end
                self.write('success')
                #send thank you email
                sender_address = "<starvingsounds-1091@appspot.gserviceaccount.com>"
                subject = "Welcome to the NewsLetter!!"
                body = 'congrats on becoming a boss'
                mail.send_mail(sender_address, email, subject, body)
                potential_signee=EmailSignee(name=name,email=email)
                potential_signee.put()

        self.response.out.write(msg)



application = webapp2.WSGIApplication([
    ('/', Home),
    ('/tempsignup', Signup),
    ('/profile', Profile),
    ('/matchups', Matchups),
    ('/emailsignup', Esf)
], debug=True)
