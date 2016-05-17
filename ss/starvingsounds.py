import os
import re
import urllib2
import json
import pdb
import logging
import csv

import webapp2
import jinja2
import cgi
from google.appengine.ext.webapp.util import run_wsgi_app


from google.appengine.ext import ndb
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.db import GqlQuery
from google.appengine.api import mail
from google.appengine.api import images

from basehandler import *
from blobhandler import *
import databaseclasses
from usersystem import *
from soundcloudsystem import *


#--------------------------Pages----------------------------------------

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

class Esf(BaseHandler):
    def get(self):
        self.render('esf.html')

    def post(self):
        msg = 'invalid email'
        email = self.request.get('email')
        if valid_email(email):
            msg = 'valid email'
            e = EmailSignee.by_email(email)
            if e:
                msg ='already on list'
            else: #vetted email: add to db, send thankyou email, and success code to front end
                #send thank you email
                sender_address = "<starvingsounds-1091@appspot.gserviceaccount.com>"
                subject = "Welcome to the Starving Sounds %s"
                body = name + ''',
                Thank you for signing up for the Starving Sounds.
                We are currently testing with artists interested in the project. While we aren't accepting any more members for the alpha right now, you are in our database and will be among the first we contact when we open up the service to more members.
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

class UploadSongs(BaseHandler):
    def uploadSong(self,songname,albumname):
        #see if albumname is None
        if albumname == 'None':
            albumquery = ndb.gql("SELECT * FROM Album WHERE name = :1 AND artist = :2", albumname,self.user.name)
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
            albumnames = self.getAlbums(self.user.key)
            upload_url = blobstore.create_upload_url('/uploadsongs')
            params = dict(name = self.user.name,
                      email = self.user.email,
                      albumnames = albumnames,
                      upurl = upload_url)
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
            albumquery = ndb.gql("SELECT * FROM Album WHERE name = :1 AND artist = :2", albumname,self.user.name)
            tempqueryrow = albumquery.get()
            if tempqueryrow is None:
                entry = Album(name=albumname,artist=self.user.name)
                entry.put()
                self.response.out.write(albumname)
            else:
                self.response.out.write('album already made')

class Mockup(BaseHandler):
    def get(self):
        self.render('mockupbase.html')

class Standings(BaseHandler):
    def get(self):
        self.render('standings.html')

class Mprofile(BaseHandler):
    def get(self):
        self.render('mockupprofile.html')      
class GetImage(BaseHandler):
    def get(self):
        i = self.request.get('id')
        img = images.Image(blob_key=i)
        img.resize(width=100, height=100)
        img.im_feeling_lucky()
        thumbnail = img.execute_transforms(output_encoding=images.PNG)
        self.response.headers['Content-Type'] = 'image/png'
        self.response.out.write(thumbnail)

application = webapp2.WSGIApplication([
    ('/', Home),
    ('/signup', Signup),
    ('/upload', Upload),
    ('/login', Login),
    ('/logout', Logout),
    ('/passwordreset', PassReset),
    ('/profile', Profile),
    ('/uploadsongs', UploadSongs),
    ('/matchups', Matchups),
    ('/emailsignup', Esf),
    ('/mockup',Mockup),
    ('/mockup/standings',Standings),
    ('/mockup/profile', Mprofile),
    ('/image', GetImage),
    ('/admin', Admin),
    ('/scmatchups', SCMatchups)
], debug=True)
