from datetime import datetime, date, time, timedelta
from google.appengine.api import memcache
from starvingsounds import *


login_session = {}

class Admin(BaseHandler):
    def get(self):
        if self.read_secure_cookie('sid'):
            secleft = self.is_session_active()
            if secleft >= 0:
                self.render('usersystem/admin.html')
            else:
                self.redirect('/login')
        else:
            self.redirect('/login')

class Signup(BaseHandler):

    def sendConfEmail(self, databaseuser):
        try:
            email = databaseuser.email
            random_bytes = os.urandom(52)
            token = base64.urlsafe_b64encode(random_bytes).decode('utf-8')
            reset_key = token[:-2]
            databaseuser.emailverified = reset_key
            databaseuser.put()
            reset_url = 'http://www.glasscapitol.com/emailconfirmation?user=%s&key=%s' % (databaseuser.username, reset_key)
            logging.info(reset_url)
            sender_address = "starvingsounds.com Email Confirmation <starvingsounds@gmail.com>"
            subject = "Email Confirmation - Starving Sounds"
            body = """Thank you for signing up with The Starving Sounds!\nWhile we set up your user account please click the following link to confirm your email address.\n\n%s\n\nThanks,\nThe Starving Sounds Team""" % (reset_url)
            mail.send_mail(sender_address, email, subject, body)
            logging.debug('sent confirmation email')
        except:
            logging.warning('failed to send confirmation email')


    def get(self):
        if self.user:
            self.redirect('/admin')
        else:
            self.render('usersystem/signupwall.html',msg = 'Enter Key')

    def post(self):
        key = self.request.get('key')
        t = self.request.get('formtype')
        logging.error(t)
        if t == 'keyform':
            key = self.request.get('key')
            if self.request.get('password') != '':
                logging.critical('honeypot detected spambot - presignup')
                self.redirect('/')
            elif key == 'nextlevel':
                self.render('usersystem/signup.html',aname='Artist Name',email='Email',password='Password',cpass='Confirm Password',city='City',state='State',quote='Quote')
        elif t == 'udata':
            error = ''
            msg = 'success'
            name = self.request.get('name')
            email = self.request.get('email')
            password = self.request.get('legit-pass')
            confirmpass = self.request.get('confirmpass')
            city = self.request.get('city')
            state = self.request.get('state')
            quote = self.request.get('quote')
            if self.request.get('password') != '':
                logging.critical('honeypot detected spambot - signup')
                self.redirect('/')
            elif (password == confirmpass):
                namequery = ndb.gql("SELECT * FROM User WHERE name = :1", name).get()
                emailquery = ndb.gql("SELECT * FROM User WHERE email = :1", email).get()
                if namequery:
                    error = error + 'name:name taken,'
                if emailquery:
                    error = error + 'email:email taken,'
                if name == '':
                    error = error + 'name:invalid name,'
                if email == '':
                    error = error + 'email:invalid email,'
                if city == '':
                    error = error + 'city:where you at,'
                if state == '':
                    error = error + 'state:which state dawg,'
                if password == '':
                    error = error + 'password:invalid password,'
                if password != '' and password!=confirmpass:
                    error = error + 'password:non matching,'
                elif error == '':
                    temp = User.register(name, email, quote, city, state, password)
                    temp.put()
                    logging.info('User created')
                    self.redirect('/login')
                    """
                    self.sendConfEmail(temp)
                    u = User.login(name,password)
                    a = User.query(User.name == name).get()
                    logging.error(a)
                    logging.error(name)
                    expr = datetime.now()+timedelta(seconds=SESSION_LENGTH)
                    uid = u.key().id()
                    sess = Session(userid = uid, expiration = expr)
                    sess.put()
                    self.login(sess, expr)"""

                else:
                    msg = error
                    self.response.out.write(msg)
        else:
            self.render('usersystem/signupwall.html',msg='Invalid Key')
                            

class Login(BaseHandler):
    def get(self):
        msg = 'Session expired, login again to continue browsing'
        if self.read_secure_cookie('sid'):
            secleft = self.is_session_active()
            if secleft >= 0:
                msg = 'Session cookie still active: '+str(secleft)+' seconds left.'
        self.render('usersystem/login.html', error = msg)

    def post(self):
        username = self.request.get('name')
        password = self.request.get('legit-pass')
        logging.error(username)
        if self.request.get('password') != '':
            logging.critical('honeypot detected spambot - login')
            self.redirect('/')
        else:
            a = User.query()
            a = a.filter(User.name == username)
            logging.error(a)
            u = User.login(username, password)
            if u:
                expr = datetime.now()+timedelta(seconds=SESSION_LENGTH)
                uid = u.key.id()
                sess = Session(userid = uid, expiration = expr)
                sess.put()
                self.login(sess, expr)
                self.redirect('/admin')
            else:
                msg = 'Invalid username or password'
                self.render('usersystem/login.html', error = msg)

class Logout(BaseHandler):
    def get(self):
        self.logout()
        self.redirect('/')

class PassReset(BaseHandler):
    def get(self):
        self.render('usersystem/lostpassword.html')

    def post(self):
        username = self.request.get('name')
        databaseuser = User.by_name(username)
        msg = ''
        if self.request.get('password') != '':
            logging.critical('honeypot detected spambot - passreset')
            self.redirect('/')
        else:
            try:
                email = databaseuser.email
                msg = 'An email will be sent to: '+str(email)
                random_bytes = os.urandom(102)
                token = base64.urlsafe_b64encode(random_bytes).decode('utf-8')
                reset_key = token[:-2]
                databaseuser.reset_code = reset_key
                databaseuser.reset_expr = datetime.now() + timedelta(seconds=3600)
                databaseuser.put()
                reset_url = 'http://www.starvingsounds.com/emailreset?user=%s&key=%s' % (username, reset_key)
                logging.info(reset_url)
                sender_address = "starvingsounds.com Password Reset <starvingsounds@gmail.com>"
                subject = "Password Reset request - Starving Sounds"
                body = """
We have received a password reset request for the user: %s.
If you created this request, please click the link below to reset your password.

%s

If you did not create this request please check to see if your account has been accessed.
If this user is not you, please disregard and delete this email.

Thank you,
The Glass Capitol Team""" % (username, reset_url)
                mail.send_mail(sender_address, email, subject, body)
            except:
                msg = 'Incorrect username'
                reset_url = ''
            self.render('usersystem/lostpassword.html', error = msg)

        
class Profile(BaseHandler, blobstore_handlers.BlobstoreDownloadHandler):
    def get(self):
        if self.user:
            params = self.getArtistInfo(self.user) 
            albumnames = self.getAlbums(self.user.name)
            songnames = self.getSongs(self.user.name)
            logging.error(songnames)
            musicparams = dict(albumnames = albumnames,songnames = songnames,profilepic=self.user.profile_picture)
            params.update(musicparams)
            self.render('usersystem/profile.html', **params)
        else:
            self.redirect('/')
