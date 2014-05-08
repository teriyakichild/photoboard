#!/usr/bin/python
import tornado.wsgi
import wsgiref.simple_server
import tornado.ioloop
import tornado.web
import tornado.auth
import tornado.gen
import tornado.options
import os.path
import uuid
from backend import pictures, boards, users
from PIL import Image

tornado.options.define("port", default="8888", help="Port")


class MainHandler(tornado.web.RequestHandler):
  def pictures(self):
    return self.application.pictures
  def boards(self):
    return self.application.boards
  def users(self):
    return self.application.users
  @tornado.web.removeslash
  @tornado.web.authenticated
  def get(self):
    self.render('index.html')
  def post(self):
    picture = self.get_argument('picture',None)
    if not picture:
      self.redirect('/')
    else:
      self.write(picture)
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
    uploads_dir = '/opt/photoboard/uploads/'
    fileinfo = self.request.files['picture'][0]
    fname = fileinfo['filename']
    extn = os.path.splitext(fname)[1]
    cname = str(uuid.uuid4()) + extn
    file_path = uploads_dir + cname
    id = self.pictures().new(file_path,self.get_current_user()['id'],board_id)
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
    self.render('new_board.html')
  def post(self):
    board_name = self.get_argument('board_name')
    board_id = self.boards().new(board_name,self.get_current_user()['id'])
    self.redirect('/boards/{0}'.format(board_id))

class BoardHandler(MainHandler):
  @tornado.web.authenticated
  def get(self,id=None):
    if id is None:
      boards = self.boards().all()
      self.render('board.html',id=id, boards=boards)
    else:
      pictures = self.pictures().all(id)
      self.render('board.html',id=id, pictures=pictures)
  @tornado.web.authenticated
  def post(self):
    board_name = self.get_argument('board_name')
    board_id = self.boards().new(board_name,self.get_current_user()['id'])
    self.redirect('/boards/{0}'.format(board_id))

class UserHandler(MainHandler):
  @tornado.web.authenticated
  def get(self):
    users=self.users().all()
    self.render('users.html',users=users)

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
    self.pictures = pictures()
    self.boards = boards()
    self.users = users()

settings = dict(
       app_title='PhotoBoard',
       template_path='/opt/photoboard/templates',
       static_path='/opt/photoboard/public',
       cookie_secret='asdfjalsdjfiowejmslkdfj',
       login_url='/login',
       debug=True)

handlers = [
    (r"/", MainHandler),
    (r"/upload", UploadHandler),
    (r"/create", NewBoardHandler),
    (r"/users", UserHandler),
    (r"/boards", BoardHandler),
    (r"/boards/([0-9]+)", BoardHandler),
    (r"/pictures/(.*)", tornado.web.StaticFileHandler, {'path': '/opt/photoboard/uploads/'}),
    (r"/public/(.*)", tornado.web.StaticFileHandler, {'path': '/opt/photoboard/public/'}),
    (r"/login", AuthLoginHandler),
    (r"/logout", AuthLogoutHandler)
]

# Parse Command Line Options
tornado.options.parse_command_line()

application = Application(handlers,settings)

if __name__ == "__main__":

  application.listen(tornado.options.options.port)
  tornado.ioloop.IOLoop.instance().start()

#  server = wsgiref.simple_server.make_server('', 8888, application)
#  server.serve_forever()
