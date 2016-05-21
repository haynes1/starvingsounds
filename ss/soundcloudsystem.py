from datetime import datetime, date, time, timedelta
from google.appengine.api import memcache
from starvingsounds import *

import soundcloud

# create client object with app credentials
client = soundcloud.Client(client_id='d24f23fb95a2edfe74edd82955f80dd0',
                   client_secret='ae7598f3b6776f51d021e36b38d62ef2',
                   redirect_uri='http://localhost:8080/sc/welcome')

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
		access_token = client.exchange_token(code)
		user = client.get('/me')
		logging.error(ScUser.by_client_id(user.client_id))
		ScUser.register(user)
		self.render('usersystem/scwelcome.html', user = user)

class SCprofile(BaseHandler):
	def get(self):
		self.render('usersystem/profile.html')