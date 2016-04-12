from datetime import datetime, date, time, timedelta
from google.appengine.api import memcache
from starvingsounds import *

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