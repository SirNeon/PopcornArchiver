from __future__ import print_function
from os.path import isfile
import re
from socket import error, timeout
import sqlite3 as db
from mechanize import Browser
import praw
from praw.errors import *
from requests.exceptions import HTTPError
from simpleconfigparser import simpleconfigparser


class SettingsError(Exception):
    """
    Gets raised when the settings.cfg file is missing.
    """


class PopcornArchiver(object):

    def __init__(self):
        self.config = simpleconfigparser()

        if not(isfile("settings.cfg")):
            raise SettingsError("Could not find settings.cfg.")
        else:
            self.config.read("settings.cfg")

        self.password = self.config.login.password
        self.verbose = self.config.main.getboolean("verbose")
        self.username = self.config.login.username


    def addMsg(self, msg=None, endchar='\n'):
        """
        Adds terminal output. Takes two optional arguments. msg defaults to None.
        msg is the message to be printed. endchar defaults to \n. endchar is the
        trailing character of the message to be printed.
        """
        if(self.verbose):
            if msg is not None:
                print(msg, end=endchar)

            
    def login(self):
        """
        This function creates a PRAW instance and logs into reddit. It uses the
        username and password specified in the config file.
        """
        self.client = praw.Reddit(user_agent="Drama archiving bot by /u/SirNeon")
        self.addMsg("Logging in as {}...".format(self.username))
        while True:
            try:
                self.client.login(self.username, self.password)
                break
            except InvalidUserName:
                print("Invalid username.")
                break
            except InvalidUserPass:
                print("Invalid password.")
                break
            except (error, HTTPError, timeout) as e:
                self.addMsg(e)
                continue
            except Exception as e:
                print(e)
                break

    def getNewSubmissions(self, subreddit_list):
        """
        """

        
    def getArchiveToday(self, links):
        """
        """

        
    def getRedditlog(self, links):
        """
        """
        

    def getWebArchive(self, links):
        """
        """


    def formatComment(self, links):
        """
        """


    def submitComment(self, text):
        """
        """


    def __addToDatabase(self, link):
        """
        """
    

def main():
    Archiver = PopcornArchiver()

    
if __name__ == '__main__':
    main()
