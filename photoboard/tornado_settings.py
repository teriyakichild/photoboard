import tornado.options

tornado.options.define('app_title', group='application')
tornado.options.define('app_dir', group='application')
tornado.options.define('cookie_secret', group='application')
tornado.options.define('debug', group='application')
tornado.options.define("port", default="8888", help="Port")
tornado.options.parse_config_file("/etc/photoboard.conf")
tornado.options.parse_command_line()

options = tornado.options.options
settings = dict(
#     autoreload='',
     db_dir = '{0}/{1}'.format(options.app_dir,'db'),
     static_path='{0}/{1}'.format(options.app_dir,'public'),
     cookie_secret=options.cookie_secret,
     login_url='/login',
     template_path='{0}/{1}'.format(options.app_dir,'templates'),
#     default_handler_class,
#     gzip,
#     log_function,
#     serve_traceback,
#     login_url,
#     autoescape,
     debug=options.debug)
