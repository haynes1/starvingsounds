import hmac
import random
import hashlib
import random, string
from string import letters
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.db import GqlQuery
from google.appengine.ext import db


secret = 'pimpsauce'
SESSION_LENGTH = 7200*36
DB_SESSION_RESET = 600
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

def valid_pw(email, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(email, password, salt)

#--------------------------DB Classes----------------------------------------

class User(ndb.Model):
    name = ndb.StringProperty(required = True)
    email = ndb.StringProperty(required = True)
    pw_hash = ndb.StringProperty(required = True)
    city = ndb.StringProperty(required = False)
    state = ndb.StringProperty(required = False)
    age = ndb.IntegerProperty(required = False)
    quote = ndb.StringProperty(required=False)
    gender = ndb.StringProperty(required = False)
    created = ndb.DateTimeProperty(required = True, auto_now = True)
    last_modified = ndb.DateTimeProperty(required = True, auto_now = True)
    token = ndb.StringProperty()
    profile_picture = ndb.BlobKeyProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid)

    @classmethod
    def by_email(cls, email):
        u = cls.query(cls.email == email).get()
        return u

    @classmethod
    def by_name(cls, name):
        u = cls.query()
        u = u.filter(cls.name == name).get()
        return u

    @classmethod
    def register(cls,name, email, quote, city, state, pw):
        pw_hash = make_pw_hash(name, pw)
        return cls( name = name,
                    email = email,
                    city = city,
                    quote = quote,
                    state = state,
                    pw_hash = pw_hash)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u

class Session(db.Model):
    userid = db.IntegerProperty(required = True)
    expiration = db.DateTimeProperty(required = True)

class EmailSignee(ndb.Model):
    created = ndb.DateTimeProperty(required = True, auto_now = True)
    email = ndb.StringProperty(required = True)
    name = ndb.StringProperty(required = True)

    @classmethod
    def by_email(cls, email):
        u = cls.all().filter('email =', email).get()
        return u

class Song(ndb.Model):
    name = ndb.StringProperty(required = True)
    artist = ndb.StringProperty(required = True)
    album = ndb.StringProperty(required = True)
    num_wins = ndb.IntegerProperty()
    num_losses = ndb.IntegerProperty()
    win_keys = ndb.IntegerProperty()
    loss_keys = ndb.StringProperty()
    win_percent = ndb.IntegerProperty()
    rank = ndb.IntegerProperty()
    created = ndb.DateTimeProperty(required = True, auto_now = True)
        

class Album(ndb.Model):
    name = ndb.StringProperty(required=True)
    artist = ndb.StringProperty(required=True)
    song_names = ndb.StringProperty()
    song_keys = ndb.StringProperty()
    privacy = ndb.StringProperty()
