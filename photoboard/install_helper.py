from photoboard.backend import boards,users,photos
from photoboard.tornado_settings import options,settings

db_dir = '{0}/{1}'.format(options.app_dir,'db')
p = photos(db_dir)
u = users(db_dir)
b = boards(db_dir)

b.init_table('CREATE TABLE if not exists boards (id integer primary key, name varchar, creator_id integer, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);')
p.init_table('CREATE TABLE if not exists photos (id integer primary key, filename varchar, user_id integer, board_id integer, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);')
u.init_table('CREATE TABLE if not exists users (id integer primary key, username varchar unique, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);')
u.init_table('CREATE TABLE if not exists access (user_id integer, board_id integer, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, CONSTRAINT unq UNIQUE (user_id, board_id));')
