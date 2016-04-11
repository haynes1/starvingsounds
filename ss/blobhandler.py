from basehandler import *

class Upload(blobstore_handlers.BlobstoreUploadHandler, BaseHandler):
    def get(self):
        self.redirect('/')
    
    def post(self):
        upload = self.get_uploads('profilepic')[0]
        blob_key=upload.key()
        u = self.user
        u.profile_picture = blob_key
        u.put()
        self.redirect('/profile')