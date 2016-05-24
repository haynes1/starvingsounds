from datetime import datetime, date, time, timedelta
from google.appengine.api import memcache
from starvingsounds import *

import soundcloud

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# create client object with app credentials
client_id = 'd24f23fb95a2edfe74edd82955f80dd0'
client_secret = 'ae7598f3b6776f51d021e36b38d62ef2'
client = soundcloud.Client(client_id=client_id,
                   client_secret=client_secret,
                   redirect_uri='http://localhost:8080/sc/welcome')

soundcloud_url = 'https://api.soundcloud.com'


class SCMatchups(BaseHandler):
    def get(self):
        if self.read_secure_cookie('sid'):
            secleft = self.is_session_active()
            if secleft >= 0:
                self.render('souncloud/scmatchups.html')
            else:
                self.redirect('/login')
        else:
            self.redirect('/login')

class SClogin(BaseHandler):
	def get(self):
		self.redirect(client.authorize_url())

class SCwelcome(BaseHandler):
	def get(self):
		code = self.request.get('code')
		token = client.exchange_token(code)
		soundcloud_user = client.get('/me')
		user = ScUser.register(soundcloud_user,token.access_token)
		if not ScUser.by_scid(user.scid):
			user.put()
			self.set_secure_cookie('scid', str(user.scid))
		self.render('usersystem/scwelcome.html', user = soundcloud_user)

class SCprofile(BaseHandler):
	def get_tracks(self,user_id):
		tracks = ScTrack.query(ScTrack.user_id == user_id)
		return tracks

	def get(self):
		scid = self.read_secure_cookie('scid')
		if scid:
			user = ScUser.by_scid(int(scid))
			if user:	
				tracklist = self.get_tracks(user.scid)
				self.render('usersystem/profile.html', user=user, tracklist=tracklist)
		else:
			self.redirect('/')

	def post(self):
		#lets get the user's tracks
		scid = self.read_secure_cookie('scid')
		if scid:
			user = ScUser.by_scid(int(scid))
			if user:
				#import songs
				user_client = soundcloud.Client(user = user.scid, access_token=user.access_token)
				tracks = client.get('users/'+str(user.scid)+'/tracks', limit=10)
				track_names = ''
				for track in tracks:
				    existing = ScTrack.query(ScTrack.song_id == track.id).get()
				    if not existing: #song already exists, don't add
				    	tobject = ScTrack.add(track)
				    	tobject.put()
				    	logging.info(vars(tobject))
				    track_names = track_names + track.title+'   ****   '

				#get tracks and render page
				tracklist = self.get_tracks(user.scid)
				self.render('usersystem/profile.html', user=user, tracklist=tracklist)
		else:
			self.redirect('/')

class SClibrary(BaseHandler):
	def get(self):
		tracklist = ScTrack.query().fetch(20)
		for track in tracklist:
			logging.error(track.title)
		self.render('soundcloud/sclibrary.html', user='None', tracklist=tracklist)

class SCplayer(BaseHandler):
	def post(self):
		track_id = self.request.get('track_id')
		track = client.get('/tracks/'+track_id)
		stream_url = client.get(track.stream_url, allow_redirects=False)
		self.write(stream_url.location)
		

		