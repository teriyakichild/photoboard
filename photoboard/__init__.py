#!/usr/bin/python
import tornado.wsgi
import wsgiref.simple_server
import tornado.ioloop
import tornado.web
import tornado.auth
import tornado.gen
import os.path
import uuid
from tornado_settings import options,settings
from backend import photos, boards, users
from PIL import Image

class MainHandler(tornado.web.RequestHandler):
  def photos(self):
    return self.application.photos
  def boards(self):
    return self.application.boards
  def users(self):
    return self.application.users
  @tornado.web.removeslash
  @tornado.web.authenticated
  def get(self):
    self.render('index.html.j2')
  def post(self):
    photos = self.get_argument('photo',None)
    if not photos:
      self.redirect('/')
    else:
      self.write(photo)
  def get_current_user(self):
      user_json = self.get_secure_cookie("photoboard_user")
      if user_json:
        data = tornado.escape.json_decode(user_json)
        check = self.users().get_by_name(data['email'])
        if check is not None:
          data['id'] = check[0]
      if not user_json: return None
      return data

class UploadHandler(MainHandler):
  @tornado.web.authenticated
  def post(self):
    board_id = self.get_argument('board_id',None)
    photos_dir = '/opt/photoboard/photos/'
    fileinfo = self.request.files['photo'][0]
    fname = fileinfo['filename']
    extn = os.path.splitext(fname)[1]
    cname = str(uuid.uuid4()) + extn
    file_path = photos_dir + cname
    id = self.photos().new(file_path,self.get_current_user()['id'],board_id)
    fh = open(file_path, 'w')
    fh.write(fileinfo['body'])
    image = Image.open(file_path)
    try:
      image.load()
    except IOError:
      pass
    resize=False
    if image.size[1] > 2000:
      resize=True
      multiplier = 10
    elif image.size[1] > 1500:
      resize=True
      multiplier = 8
    elif image.size[1] > 1000:
      resize=True
      multiplier = 6
    elif image.size[1] > 500:
      resize=True
      multiplier = 3
    if resize:
      newsize = tuple([i/multiplier for i in image.size])
      new = image.resize(newsize,Image.ANTIALIAS)
      new.save(file_path,optimize=True,quality=95)
    self.redirect('/boards/{0}'.format(board_id))


class NewBoardHandler(MainHandler):
  @tornado.web.authenticated
  def get(self):
    self.render('new_board.html.j2')
  def post(self):
    board_name = self.get_argument('board_name')
    board_id = self.boards().new(board_name,self.get_current_user()['id'])
    self.redirect('/boards/{0}'.format(board_id))

class BoardHandler(MainHandler):
  @tornado.web.authenticated
  def get(self,id=None):
    if id is None:
      boards = self.boards().all()
      self.render('board.html.j2',id=id, boards=boards)
    else:
      photos = self.photos().all(id)
      self.render('board.html.j2',id=id, photos=photos)
  @tornado.web.authenticated
  def post(self):
    board_name = self.get_argument('board_name')
    board_id = self.boards().new(board_name,self.get_current_user()['id'])
    self.redirect('/boards/{0}'.format(board_id))

class UserHandler(MainHandler):
  @tornado.web.authenticated
  def get(self):
    users=self.users().all()
    self.render('users.html.j2',users=users)

class AuthLoginHandler(MainHandler, tornado.auth.GoogleMixin):
    @tornado.gen.coroutine
    def get(self):
        if self.get_argument("openid.mode", None):
            user = yield self.get_authenticated_user()
            self.set_secure_cookie("photoboard_user",tornado.escape.json_encode(user))
            check = self.users().get_by_name(user['email'])
            if check is None:
              self.users().new(user['email'])
            self.redirect("/")
            return
        self.authenticate_redirect()

class AuthLogoutHandler(MainHandler):
    def get(self):
        self.clear_cookie("photoboard_user")
        self.redirect(self.get_argument("next", "/"))

class Application(tornado.web.Application):
  def __init__(self,handlers,settings):
    tornado.web.Application.__init__(self, handlers, **settings)
    # Initialize backend services
    self.photos = photos(settings['db_dir'])
    self.boards = boards(settings['db_dir'])
    self.users = users(settings['db_dir'])

def main():

  handlers = [
    (r"/", MainHandler),
    (r"/upload", UploadHandler),
    (r"/create", NewBoardHandler),
    (r"/users", UserHandler),
    (r"/boards", BoardHandler),
    (r"/boards/([0-9]+)", BoardHandler),
    (r"/photos/(.*)", tornado.web.StaticFileHandler, {'path': '{0}/{1}/'.format(options.app_dir,'photos')}),
    (r"/public/(.*)", tornado.web.StaticFileHandler, {'path': '{0}'.format(settings['static_path'])}),
    (r"/login", AuthLoginHandler),
    (r"/logout", AuthLogoutHandler)
  ]         

  application = Application(handlers,settings)

  application.listen(options.port)
  tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
  main()

