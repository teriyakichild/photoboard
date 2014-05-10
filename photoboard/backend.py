import sqlite3

class photos:
    def __init__(self,db_dir):
        self.conn = sqlite3.connect('{0}/stuff.db'.format(db_dir))
        self.db = self.conn.cursor()
    def init_table(self,table_query):
        self.db.execute(table_query)
        self.conn.commit()
        return
    def all(self,board_id):
        self.db.execute("SELECT * FROM photos join users on photos.user_id = users.id where board_id = ? order by id desc limit 10;", (board_id,))
        tmp = self.db.fetchall()
        photos = []
        for photo in tmp:
          ret = { 'id': photo[0],
                  'filename': photo[1].split('/')[4],
                  'username': photo[6]
                }
          photos.append(ret)
        return photos
    def new(self,filename,user_id,board_id):
        try:
          self.db.execute("INSERT INTO photos (filename,user_id,board_id) VALUES (?,?,?)", (filename,user_id,board_id,))
        except sqlite3.IntegrityError:
          return None
        self.conn.commit()
        return self.db.lastrowid
    def get(self,id):
        self.db.execute("SELECT * FROM photos join users on photos.user_id = users.id where photos.id = ?", (id,))
        photo = self.db.fetchone()
        ret = { 'id': photo[0],
                'filename': photo[1].split('/')[4],
                'user_id': photo[6],
                'board_id': photo[3]
              }
        return ret

class boards:
    def __init__(self,db_dir):
        self.conn = sqlite3.connect('{0}/stuff.db'.format(db_dir))
        self.db = self.conn.cursor()
    def init_table(self,table_query):
        self.db.execute(table_query)
        self.conn.commit()
        return
    def all(self):
        self.db.execute("SELECT * FROM boards;")
        boards = self.db.fetchall()
        return boards
    def all_for_user(self,user):
        self.db.execute("SELECT * FROM boards;")
        boards = self.db.fetchall()
        return boards
    def new(self,name,creator_id):
        try:
          self.db.execute("INSERT INTO boards (name,creator_id) VALUES (?,?)", (name,creator_id,))
        except sqlite3.IntegrityError:
          return None
        self.conn.commit()
        return self.db.lastrowid
    def get(self,id):
        self.db.execute("SELECT * FROM boards where id = ?", (id,))
        board = self.db.fetchone()
        return board

class users:
    def __init__(self,db_dir):
        self.conn = sqlite3.connect('{0}/stuff.db'.format(db_dir))
        self.db = self.conn.cursor()
    def init_table(self,table_query):
        status = self.db.execute(table_query)
        self.conn.commit()
        return status
    def all(self):
        self.db.execute("SELECT * FROM users;")
        users = self.db.fetchall()
        return users
    def new(self,username):
        try:
          self.db.execute("INSERT INTO users (username) VALUES (?)", (username,))
        except sqlite3.IntegrityError:
          return None
        self.conn.commit()
    def get_by_id(self,id):
        self.db.execute("SELECT * FROM users where id = ?", (id,))
        user = self.db.fetchone()
        return user
    def get_by_name(self,username):
        self.db.execute("SELECT * FROM users where username = ?", (username,))
        user = self.db.fetchone()
        return user


if __name__ == "__main__":
  print '############## TESTING PICTURES #########################'
  photos = photos()
  print photos.all(1)
  print photos.get(1)
#  print photos.new('asdf',1,1)
  print '############## TESTING BOARDS #########################'
  boards = boards()
  print boards.all()
#  print boards.new('asdf',1)
#  print photos.new('asdf2',1,1)
