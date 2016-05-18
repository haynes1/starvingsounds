from datetime import datetime, date, time, timedelta
from google.appengine.api import memcache
from starvingsounds import *

import soundcloud

# create client object with app credentials
client = soundcloud.Client(client_id='8f895010fb144572d60abc787476c2e9',
                           client_secret='5c46706dedc4892e424e71a0b7508231',
                           redirect_uri='http://starvingsounds.com/sc/profile')

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

class SCprofile(BaseHandler):
	def get(self):
		code = self.request.get('code')
		access_token = client.exchange_token(code)
		self.write('Profile success!!!')