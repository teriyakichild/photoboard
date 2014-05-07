import sqlite3
import os.path

class pictures:
    def __init__(self):
        self.conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.realpath(__file__)),'db/stuff.db'))
        self.db = self.conn.cursor()
    def all(self,board_id):
        self.db.execute("SELECT * FROM pictures join users on pictures.user_id = users.id where board_id = ? order by id desc limit 10;", (board_id,))
        tmp = self.db.fetchall()
        pictures = []
        for picture in tmp:
          ret = { 'id': picture[0],
                  'filename': picture[1].split('/')[4],
                  'username': picture[6]
                }
          pictures.append(ret)
        return pictures
    def new(self,filename,user_id,board_id):
        try:
          self.db.execute("INSERT INTO pictures (filename,user_id,board_id) VALUES (?,?,?)", (filename,user_id,board_id,))
        except sqlite3.IntegrityError:
          return None
        self.conn.commit()
        return self.db.lastrowid
    def get(self,id):
        self.db.execute("SELECT * FROM pictures join users on pictures.user_id = users.id where pictures.id = ?", (id,))
        picture = self.db.fetchone()
        ret = { 'id': picture[0],
                'filename': picture[1].split('/')[4],
                'user_id': picture[6],
                'board_id': picture[3]
              }
        return ret

class boards:
    def __init__(self):
        self.conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.realpath(__file__)),'db/stuff.db'))
        self.db = self.conn.cursor()
    def all(self):
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
    def __init__(self):
        self.conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.realpath(__file__)),'db/stuff.db'))
        self.db = self.conn.cursor()
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
  pictures = pictures()
  print pictures.all(1)
  print pictures.get(1)
#  print pictures.new('asdf',1,1)
  print '############## TESTING BOARDS #########################'
  boards = boards()
  print boards.all()
#  print boards.new('asdf',1)
#  print pictures.new('asdf2',1,1)
