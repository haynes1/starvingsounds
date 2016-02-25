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

secret = 'pimpsauce'
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
    name = db.StringProperty(required = True)
    email = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    city = db.StringProperty(required = False)
    state = db.StringProperty(required = False)
    age = db.IntegerProperty(required = False)
    gender = db.StringProperty(required = False)
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
    def by_name(cls, name):
        u = cls.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls,name, email, city, state, pw):
        pw_hash = make_pw_hash(name, pw)
        return cls( name = name,
                    email = email,
                    city = city,
                    state = state,
                    pw_hash = pw_hash)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u:
            return u

class EmailSignee(db.Model):
    created = db.DateTimeProperty(required = True, auto_now = True)
    email = db.StringProperty(required = True)
    name = db.StringProperty(required = True)

    @classmethod
    def by_email(cls, email):
        u = cls.all().filter('email =', email).get()
        return u

class Song(db.Model):
    name = db.StringProperty(required = True)
    artist = db.StringProperty(required = True)
    album = db.StringProperty(required = True)
    num_wins = db.IntegerProperty()
    num_losses = db.IntegerProperty()
    win_keys = db.IntegerProperty()
    loss_keys = db.StringProperty()
    win_percent = db.IntegerProperty()
    rank = db.IntegerProperty()
    created = db.DateTimeProperty(required = True, auto_now = True)
        

class Album(db.Model):
    name = db.StringProperty(required=True)
    artist = db.StringProperty(required=True)
    song_names = db.StringProperty()
    song_keys = db.StringProperty()
    privacy = db.StringProperty()



#--------------------------Pages----------------------------------------
class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
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
        self.user = uid and User.by_id(int(uid))

    def getAlbums(self, user):
        ret='album1&&&album2&&&album3'
        albumquery = GqlQuery("SELECT name FROM Album WHERE artist = :1", user)
        tempqueryrow = albumquery.get()
        if tempqueryrow is None:
            ret = 'None'
        return ret

    def getSongs(self, user):
        ret='song1;;;song2;;;song3'
        songquery = GqlQuery("SELECT name FROM Song WHERE artist = :1", user)
        tempqueryrow = songquery.fetch(20)
        if len(tempqueryrow) == 0:
            logging.error('HAHAHAHAHAHAHAHAHA')
            ret = """Caught up in the process$$$1,073$$$98%\nGenius$$$968$$$98%\nNeezus$$$3,621$$$96%\nMy Life$$$4,802$$$96%\nFeeling Some Way$$$2,331$$$95%\nThat Guala$$$4,873$$$95%\nState of Mind$$$3,880$$$94%\nFree Man$$$5,003$$$94%"""
        else:
            songstring=''
            for r in tempqueryrow:
                logging.error(r)
                songstring = songstring  + r.name + '\n'
            ret = songstring      
        return ret
        

class Home(BaseHandler):

    def get(self):
        self.render('home.html')

    def post(self):
        self.render('home.html')

class Matchups(BaseHandler):
    matchup1 = '1;Griz,Fine Way To Die,11,2,18,3,finewaytodie.mp3;Chemical Brothers,Galvanize,11,3,15,2,galvanize.mp3'
    matchup2 = '2;Jungle,Busy Earning,11,1,17,3,BusyEarnin.mp3;Griz,Stop Trippin,12,1,18,3,StopTrippin.mp3'
    matchup3 = '3;Kendrick Lamar,Blacker The Berry,10,1,12,1,BlackerTheBerry.mp3;Jay Z,Justify My Thug,9,1,15,2,JustifyMyThug.mp3'
    matchup4 = '0;Jungle,Time,10,2,17,3,Time.mp3;Mark E Bassy,Relapse,8,2,10,3,Relapse.mp3'
    
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
        if self.user:
            self.redirect('/profile')
        else:
            self.render('signupwall.html')


    def post(self):
        key = self.request.get('key')
        logging.error(key)
        if key == 'is you is':
            self.render('signup.html')
        elif key != '':
            self.render('signupwall.html')
        else:
            logging.error('+++++++++++++COMMING IN')
            name = self.request.get('name')
            email = self.request.get('email')
            city = self.request.get('city')
            state = self.request.get('state')
            password = self.request.get('password')
            #ensure that the user is a new user
            namequery = GqlQuery("SELECT * FROM User WHERE name = :1", name)
            namequeryrow = namequery.get()
            emailquery = GqlQuery("SELECT * FROM User WHERE email = :1", email)
            emailqueryrow = emailquery.get()
            logging.error('+++++++++++++COMMING IN 1')
            if namequeryrow is None and emailqueryrow is None:
                logging.error('+++++++++++++COMMING IN MADE IT')
                if name and email and city and state and password:
                    u = User.register(name,email,city,state,password)
                    u.put()
                    self.login(u)
                    self.response.out.write('success')
                    self.redirect('/profile')
            else:
                self.response.out.write('failure')

class Login(BaseHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        name = self.request.get('name')
        password = self.request.get('password')
        u = User.login(name, password)
        if u:
            self.login(u)
            self.response.out.write('success')
        else:
            msg = 'Invalid login'
            self.response.out.write(msg)
        
class Profile(BaseHandler):
    def get(self):
        if self.user:
            albumnames = self.getAlbums(self.user.name)
            songnames = self.getSongs(self.user.name)
            logging.error(songnames)
            params = dict(name = self.user.name,
                      email = self.user.email,
                      albumnames = albumnames,
                      songnames = songnames)
            self.render('profile.html', **params)
        else:
            self.redirect('/')

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
            else: #vetted email: add to db, send thankyou email, and success code to front end
                #send thank you email
                sender_address = "<starvingsounds-1091@appspot.gserviceaccount.com>"
                subject = "Welcome to the Starving Sounds Newsletter"
                body = name + ''',
                Thank you for signing up for the Starving Sounds Newsletter.
                You'll get first access to all features we drop, and be the first to know our launch date.
                We're still in development right now, and there will be big changes in the coming weeks and months
                Sincerely,

                Nick Abbott and Alexander Haynes

                Nick Abbott: Founder, Lead Designer, Manager
                Alexander Haynes: Cofounder, Lead Developer
                '''
                mail.send_mail(sender_address, email, subject, body)
                potential_signee=EmailSignee(name=name,email=email)
                potential_signee.put()
                msg='success'

        self.response.out.write(msg)

class Upload(BaseHandler):
    def uploadSong(self,songname,albumname):
        #see if albumname is None
        if albumname == 'None':
            albumquery = GqlQuery("SELECT * FROM Album WHERE name = :1 AND artist = :2", albumname,self.user.name)
            tempqueryrow = albumquery.get()
            if tempqueryrow is None:
                entry = Album(name='no-album',artist=self.user.name)
                entry.put()
            entry = Song(name=songname,artist=self.user.name,album='no-album')
            entry.put()
            return 'success'

    def get(self):
        if self.user: 
            #get album names
            albumnames = self.getAlbums(self.user.key())
            logging.error(albumnames)
            params = dict(name = self.user.name,
                      email = self.user.email,
                      albumnames = albumnames)
            self.render('upload.html', **params)
        else:
            self.redirect('/')

    def post(self):
        get = self.request.get('get')
        user = self.request.get('user')
        if get == 'album' and user == 'self':
            self.response.out.write('album names&&&album keys')
        elif get == 'song':
            trackname = self.request.get('songname')
            albumname = self.request.get('albumname')
            upsuccess = self.uploadSong(trackname,albumname)
            if upsuccess == 'success':
                songs = self.getSongs(self.user.name)
                logging.error(songs)
                self.response.out.write(songs)

        elif get == 'album':
            albumname = self.request.get('albumtitle')
            privacy = self.request.get('privacy')
            albumquery = GqlQuery("SELECT * FROM Album WHERE name = :1 AND artist = :2", albumname,self.user.name)
            tempqueryrow = albumquery.get()
            if tempqueryrow is None:
                entry = Album(name=albumname,artist=self.user.name)
                entry.put()
                self.response.out.write(albumname)
            else:
                self.response.out.write('album already made')

        

application = webapp2.WSGIApplication([
    ('/', Home),
    ('/tempsignup', Signup),
    ('/login', Login),
    ('/profile', Profile),
    ('/upload', Upload),
    ('/matchups', Matchups),
    ('/emailsignup', Esf)
], debug=True)
