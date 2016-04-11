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


from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.db import GqlQuery
from google.appengine.api import mail
from google.appengine.api import images

from databaseclasses import *

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
        self.set_secure_cookie('user_id', str(user.key.id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

    def getArtistInfo(self, user):
        artistinfo = dict(artistname = user.name,
                artistprofilepic = user.profile_picture,
                artistquote = user.quote,
                artistcity = user.city,
                artiststate = user.state)
        return artistinfo


    def getAlbums(self, user):
        ret='album1&&&album2&&&album3'
        albumquery = ndb.gql("SELECT name FROM Album WHERE artist = :1", str(user))
        tempqueryrow = albumquery.get()
        if tempqueryrow is None:
            ret = 'None'
        return ret

    def getSongs(self, user):
        ret='song1;;;song2;;;song3'
        songquery = ndb.gql("SELECT name FROM Song WHERE artist = :1", user)
        tempqueryrow = songquery.fetch(20)
        if len(tempqueryrow) == 0:
            ret = """Caught up in the process$$$1,073$$$98%\nGenius$$$968$$$98%\nNeezus$$$3,621$$$96%\nMy Life$$$4,802$$$96%\nFeeling Some Way$$$2,331$$$95%\nThat Guala$$$4,873$$$95%\nState of Mind$$$3,880$$$94%\nFree Man$$$5,003$$$94%"""
        else:
            songstring=''
            for r in tempqueryrow:
                logging.error(r)
                songstring = songstring  + r.name + '\n'
            ret = songstring      
        return ret
        
