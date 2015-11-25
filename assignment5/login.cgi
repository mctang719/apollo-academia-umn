#!/usr/bin/python

import cgi
import os
import Cookie
import ConfigParser

from shared import *

import cgitb
cgitb.enable()

import MySQLdb

class Database:
    def __init__(self):
        self.db = None # global variable that will hold the database reference
        self.host = None # str
        self.port = None # int
        self.user = None # str
        self.passwd = None #str
        self.db_name = None #str
        self.cookie_expiration = None # int
        
        self.readConfigFile('config') #populates the database
        self.connectAndSelectDB()

    def readConfigFile(self,filename):
        # read information from config file
        Config = ConfigParser.ConfigParser()
        Config.read(filename)
        self.host = Config.get('Database', 'host')
        self.port = Config.getint('Database', 'port')
        self.user = Config.get('Database', 'user')
        self.passwd = Config.get('Database', 'passwd')
        self.db_name = Config.get('Database', 'db_name')
        self.cookie_expiration = Config.getint('Database','cookie_expiration')

    def connectAndSelectDB(self):
        self.db = MySQLdb.connect(host=self.host, user=self.user, 
                             passwd=self.passwd, port=self.port)
        self.db.select_db(self.db_name)
        return True

    def runQuery(self, query, args):
        """Each Row is checked to be unique before insertion,
        even if adding return at most one so fetchone only.
        args must be a tuple, that holds the string formats.
        avoids sql injection. (Previous Version did not have this)
        http://bobby-tables.com/python.html
        """
        cursor = self.db.cursor()
        cursor.execute(query, args)
        result = cursor.fetchone()
        cursor.close()
        return result

    def login(self, username, passwd):
        """Since username is unique before adding into the DB 
        we don't have to check for it here."""
        result = self.runQuery(("SELECT * FROM Users "
                                "WHERE Name=%s AND Password=%s"),
                               (username, passwd))
	if result is None:
	   return False
        return True
    
    def addUser(self, username, password):
        """Only have new visitor roles, no more Owners."""

        exists = self.runQuery("SELECT * FROM Users "
                               "WHERE Name=%s", username)
        if exists is not None:
            return False

        result = self.runQuery("INSERT INTO Users "
                               "(Name, Role, Password) "
                               "VALUES (%s, 'Visitor',%s)")
        if result is not None:
            return False # failed
        return True # success

    
    def isOwner(self, username):
        result = self.runQuery("SELECT Role FROM Users WHERE Name=%s", username)
        return 'Owner' in result

    def changePassword(self, username, password):
        #Where will the field to change pwd be
        raise NotImplementedError()
        
    def deleteUser(self,username):
        if self.isOwner(username):
            return False
        result = self.runQuery("DELETE FROM Users WHERE Name=%s LIMIT 1",(username))
        print "DELETE"
        print result
        return True
    
    def makeCookie(self, username):
        cookie = Cookie.SimpleCookie()
        cookie['username'] = username
        cookie['login'] = True
        for key, morsel in cookie.iteritems():
            morsel['max-age'] = self.cookie_expiration
        print cookie # this is how you actually 'save' it LOL 
        # Credit: http://raspberrywebserver.com/cgiscripting/using-python-to-set-retreive-and-clear-cookies.html
        return True

# Returns a boolean on whether the user is already logged in, done by checking cookies
def isLoggedIn():
    cookie_str = os.environ.get('HTTP_COOKIE')
    if not cookie_str:
        return False
    cookie = Cookie.SimpleCookie()
    cookie.load(cookie_str)
    if cookie.get('login') is None:
        return False
    return cookie['login'].value == 'True'

# This is meeded since the landing page is login.html and there's no way to edit the static page. 
login_form = """
<form name="loginForm" action="login.cgi" method="POST" enctype="multipart/form-data">
 %s
 Username: <input type='text' name='username' />
 <br/>
 Password: <input type='password' name='password' />
 <br/>
<input type="submit" value="Log In" />
</form>
"""

msg = """<div id="message">Error: Invalid Username and/or Password. </div>"""
empty_msg = """<div id="message">Error: Please enter a username and password. </div>"""

def main():
    form = cgi.FieldStorage()

    if os.environ['REQUEST_METHOD'] == 'GET':
        # check if logged in
        if not isLoggedIn():
            REDIRECT('login.html')
        else:
            REDIRECT('gallery.cgi')
    else:
        db = Database()
        # Check for password or provide error (This is POST)
        username = form['username'].value
        password = form['password'].value
        if len(username) == 0 or len(password) ==0: 
            print HTML_TEMPLATE % {'windowTitle': 'Login Form', 
                                   'title' : 'Login', 
                                   'body' : (login_form % empty_msg) }
        else:
            if db.login(username, password): 
                db.makeCookie(username)
                REDIRECT('gallery.cgi')
            else:
                print HTML_TEMPLATE % {'windowTitle': 'Login Form', 
                                       'title' : 'Login', 
                                       'body' : (login_form % msg) }

main() # simple invocation