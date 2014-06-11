#!/usr/bin/python
import functools
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


def authorized(method):
    """Decorate methods with this to require that the user be logged in.

    If the user is not logged in, they will be redirected to the configured
    `login url <RequestHandler.get_login_url>`.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            if self.request.method in ("GET", "HEAD"):
                url = self.get_login_url()
                if "?" not in url:
                    if urlparse.urlsplit(url).scheme:
                        # if login url is absolute, make next absolute too
                        next_url = self.request.full_url()
                    else:
                        next_url = self.request.uri
                    url += "?" + urlencode(dict(next=next_url))
                self.redirect(url)
                return
            raise tornado.web.HTTPError(403)
        if len(args) == 1:
            if int(args[0]) not in  [board[0] for board in self.users().boards(self.current_user['id'])]:
                raise tornado.web.HTTPError(403)
        return method(self, *args, **kwargs)
    return wrapper


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
    def write_error(self, status_code, **kwargs):
        self.render('custom_error.html.j2',status_code=status_code)

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
    @authorized
    def get(self,id=None):
        if id is None:
            boards = self.boards().all_for_user(self.current_user['id'])
            self.render('board.html.j2',id=id, boards=boards)
        else:
            if int(id) == self.boards().get(id)[0]:
                photos = self.photos().all(id)
                self.render('board.html.j2',id=id, photos=photos)
            else:
                raise tornado.web.HTTPError(404)
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

class CatchAllHandler(MainHandler):
    def get(self,args,**kwargs):
       self.set_status(404)
       self.render('custom_error.html.j2',status_code=404)

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
    (r"/logout", AuthLogoutHandler),
    (r'^/(.*)$', CatchAllHandler)
  ]         

  application = Application(handlers,settings)

  application.listen(options.port)
  tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
  main()

