from datetime import datetime, date, time, timedelta
from google.appengine.api import memcache
from starvingsounds import *


class Admin(BaseHandler):
    def get(self):
        self.render('usersystem/admin.html')

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
            self.redirect('usersystem/profile')
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
                    self.sendConfEmail(temp)
                    u = User.login(name,password)
                    a = User.query(User.name == name).count()
                    logging.error(a)
                    logging.error(name)
                    expr = datetime.now()+timedelta(seconds=SESSION_LENGTH)
                    uid = temp.key().id()
                    sess = Session(userid = uid, expiration = expr)
                    sess.put()
                    self.login(sess, expr)
                    self.redirect('/admin')
                else:
                    msg = error
                    self.response.out.write(msg)
        else:
            self.render('usersystem/signupwall.html',msg='Invalid Key')
                            
class Login(BaseHandler):
    def get(self):
        self.render('usersystem/login.html')

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
