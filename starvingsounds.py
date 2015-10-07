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

#------------------------File Processing----------------------------
def process_senator_csv(blob_info):
    blob_reader = blobstore.BlobReader(blob_info.key())
    reader = csv.reader(blob_reader, delimiter='\n')
    for row in reader:
        row_str = row[0]
        id, state, rank, name, gender, party, fyio, fbid, twid, ployalty, enacted, sponsored, cosponsored, li = row_str.split(',')
        entry = Senator(bioguide_id=id, state=state, rank=rank, name=name.decode('latin-1'), gender=gender, party=party, fyio=int(fyio), fbid=fbid, twid=twid, ployalty=int(ployalty), enacted=int(enacted), sponsored=int(sponsored), cosponsored=int(cosponsored), li=int(li))
        entry.put()

def process_rep_csv(blob_info):
    blob_reader = blobstore.BlobReader(blob_info.key())
    reader = csv.reader(blob_reader, delimiter='\n')
    for row in reader:
        row_str = row[0]
        id, state, district, name, gender, party, fyio, fbid, twid, ployalty, enacted, sponsored, cosponsored, li = row_str.split(',')
        entry = Representative(bioguide_id=id, state=state, district=int(district), name=name.decode('latin-1'), gender=gender, party=party, fyio=int(fyio), fbid=fbid, twid=twid, ployalty=int(ployalty), enacted=int(enacted), sponsored=int(sponsored), cosponsored=int(cosponsored), li=int(li))
        entry.put()

#-------------------------Database Classes-----------------------------

class Senator(db.Model):
    bioguide_id = db.StringProperty(required = True)
    state = db.StringProperty(required = True)
    rank = db.StringProperty(required = True)
    name = db.StringProperty(required = True)
    gender = db.StringProperty(required = True)
    party = db.StringProperty(required = True)
    fyio = db.IntegerProperty(required = True)
    fbid = db.StringProperty(required = True)
    twid = db.StringProperty(required = True)
    ployalty = db.IntegerProperty(required = True)
    enacted = db.IntegerProperty(required = True)
    sponsored = db.IntegerProperty(required = True)
    cosponsored = db.IntegerProperty(required = True)
    li = db.IntegerProperty(required = True)

class Representative(db.Model):
    bioguide_id = db.StringProperty(required = True)
    state = db.StringProperty(required = True)
    district = db.IntegerProperty(required = True)
    name = db.StringProperty(required = True)
    gender = db.StringProperty(required = True)
    party = db.StringProperty(required = True)
    fyio = db.IntegerProperty(required = True)
    fbid = db.StringProperty(required = True)
    twid = db.StringProperty(required = True)
    ployalty = db.IntegerProperty(required = True)
    enacted = db.IntegerProperty(required = True)
    sponsored = db.IntegerProperty(required = True)
    cosponsored = db.IntegerProperty(required = True)
    li = db.IntegerProperty(required = True)

class DatastoreFile(db.Model):
  data = db.BlobProperty(required=True)
  mimetype = db.StringProperty(required=True)

#--------------------------Pages----------------------------------------
class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def get_politician_ids(self,dist):
        state, district = dist.split(':')
        s = GqlQuery('SELECT senior_senator, junior_senator FROM State WHERE abbreviation=:1', state).get()
        q = District.all()
        q.filter('state', state)
        h = q.filter('num', 3).get()
        politicians = dict(ss=s.senior_senator, js=s.junior_senator, hr=h.representative)
        return politicians

    def getHr(self, dist):
        #returns a dictionary with the basic info for the representative of district=dist
        state, district = dist.split(':')
        rep = GqlQuery('SELECT * FROM Representative WHERE state=\'%s\' and district=%s' %(state, district)).get()
        hr = dict(hrbioguideid = rep.bioguide_id,
                hrstate = rep.state,
                hrdistrict = rep.district,
                hrname = rep.name.replace('_', ' '),
                hrgender = rep.gender,
                hrparty = rep.party,
                hrfyio = rep.fyio,
                hrfbid = rep.fbid,
                hrtwid = rep.twid,
                hrployalty = rep.ployalty,
                hrenacted = rep.enacted,
                hrsponsored = rep.sponsored,
                hrcosponsored = rep.cosponsored,
                hrli = rep.li)
        return hr

    def getSs(self, dist):
        #returns a dictionary with the basic info for the representative of district=dist
        state, district = dist.split(':')
        rep = GqlQuery('SELECT * FROM Senator WHERE state=\'%s\' and rank=\'S\'' %(state)).get()
        ss = dict(ssbioguideid = rep.bioguide_id,
                ssstate = rep.state,
                ssrank = 'S',
                ssname = rep.name.replace('_', ' '),
                ssgender = rep.gender,
                ssparty = rep.party,
                ssfyio = rep.fyio,
                ssfbid = rep.fbid,
                sstwid = rep.twid,
                ssployalty = rep.ployalty,
                ssenacted = rep.enacted,
                sssponsored = rep.sponsored,
                sscosponsored = rep.cosponsored,
                ssli = rep.li)
        return ss

    def getJs(self, dist):
        #returns a dictionary with the basic info for the representative of district=dist
        state, district = dist.split(':')
        rep = GqlQuery('SELECT * FROM Senator WHERE state=\'%s\' and rank=\'J\'' %(state)).get()
        js = dict(jsbioguideid = rep.bioguide_id,
                jsstate = rep.state,
                jsrank = 'J',
                jsname = rep.name.replace('_', ' '),
                jsgender = rep.gender,
                jsparty = rep.party,
                jsfyio = rep.fyio,
                jsfbid = rep.fbid,
                jstwid = rep.twid,
                jsployalty = rep.ployalty,
                jsenacted = rep.enacted,
                jssponsored = rep.sponsored,
                jscosponsored = rep.cosponsored,
                jsli = rep.li)
        return js

class UploadHandler(webapp2.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/upload')
 
        html_string = """
         <form action="%s" method="POST" enctype="multipart/form-data">
        Upload File:
        <input type="file" name="file"> <br>
        <input type="submit" name="submit" value="Submit">
        </form>""" % upload_url
 
        self.response.out.write(html_string)

class Upload(blobstore_handlers.BlobstoreUploadHandler):

    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        info = upload_files[0]
 
        #process_senator_csv(info)
        process_rep_csv(info)
        self.redirect("/")

class Cards(BaseHandler):
    def get_legislators(self, district):
        state, dnum = district.split(':')
        #query the datastore to get the house representative
        msg = "SELECT name, party, fyio FROM Representative WHERE State=\'%s\' AND district=\'%d\'" %(state, int(dnum))
        logging.error(msg)
        q = db.GqlQuery(msg)

    def get(self):
        self.render('big3.html')

    def post(self):
        district = self.request.get('district')
        if district: #pull legislator data, and render cards with data
            self.get_legislators(district)
            hrparams = self.getHr(district)
            ssparams = self.getSs(district)
            jsparams = self.getJs(district)
            params = dict(district = district)
            params.update(hrparams)
            params.update(ssparams)
            params.update(jsparams)
            self.render('cards.html', **params)
        else:
            self.render('big3.html')

class JsonTest(BaseHandler):
    def get(self):
        self.render('sbaby.html')


application = webapp2.WSGIApplication([
    ('/', JsonTest),
    ('/up', UploadHandler),
    ('/upload', Upload),
    ('/cards', Cards)
], debug=True)
