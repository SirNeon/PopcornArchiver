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

        self.subreddit_list = list(set(self.config.main.subreddits.split(',')))

        # I figured a multireddit would be the fastest way to get new posts from
        # multiple subreddits since they can be scraped together instead of 1 by 1
        self.multireddit = ""
        for subreddit in self.subreddit_list:
            self.multireddit += subreddit + '+'

        self.multireddit = self.multireddit.strip('+')

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
        username and password specified in the config file. Returns True if successful
        and returns False if it could not log into reddit.
        """
        self.client = praw.Reddit(user_agent="Drama archiving bot by /u/SirNeon")
        self.addMsg("Logging in as {}...".format(self.username))
        success = True
        
        while True:
            try:
                self.client.login(self.username, self.password)
                break
            except InvalidUserName:
                print("Invalid username.")
                success = False
                break
            except InvalidUserPass:
                print("Invalid password.")
                success = False
                break
            except (error, HTTPError, timeout) as e:
                self.addMsg(e)
                continue
            except Exception as e:
                print(e)
                success = False
                break

        return success

            
    def getNewSubmissions(self):
        """
        This function grabs submissions from a multireddit with the specified
        subreddits in the settings.cfg file.
        """

        while True:
            try:
                submissions = self.client.get_subreddit(self.multireddit).get_new(limit=25)
                break
            except (error, HTTPError, timeout) as e:
                self.addMsg(e)
                continue

        for submission in submissions:
            __findLinks(submission)

            
    def __findLinks(self, submission):
        """
        Finds reddit links in submissions. Takes one parameter: the submission object.
        Returns a list of links if the submission is a self-post. Returns a link if the
        submission is a a link-post. Returns None if it doesn't find any reddit links or
        if an AttributeError occurs.
        """

        # this matches links to reddit submissions
        reddit_urls = re.compile("https?\:\/\/[\w.]+reddit\.com\/r\/\w+\/[\w/]+")

        try:
            self_post = submission.is_self
        except AttributeError as e:
            self.addMsg(e)
            return None

        if(self_post):
            try:
                submission_text = str(submission.selftext)
            except AttributeError as e:
                self.addMsg(e)
                return None

            links = reddit_urls.findall(submission_text)

            if links != []:
                links = __removeNoParticipation(links)
                return links

            else:
                return None

        else:
            try:
                submission_url = str(submission.url)
            except AttributeError as e:
                self.addMsg(e)
                return None

            if reddit_urls.match(submission_url) is not None:
                link = __removeNoParticipation(submission_url)
                return link

            else:
                return None


    def __removeNoParticipation(self, link=None, links=None):
        """
        Turns NP links into regular www links. Takes a parameter: either a string
        with a single link or a list with multiple links in it. Returns either a
        string with the link or a list with the new links.
        """

        if links is not None:
            if type(links) is list:
                for link in links:
                    # so that the archives will be listed in order of appearance later
                    position = links.index(link)

                    if "np.reddit.com" in link:
                        links.remove(link)
                        link = link.replace("np.reddit.com", "www.reddit.com")
                        links.insert(position, link)

                    if "www.np.reddit.com" in link:
                        links.remove(link)
                        link = link.replace("www.np.reddit.com")
                        links.insert(position, link)

                return links

            else:
                raise TypeError("Parameter \"links\" must be a list.")

        if link is not None:
            if type(link) is str:
                if "np.reddit.com" in link:
                    link = link.replace("np.reddit.com", "www.reddit.com")

                if "www.np.reddit.com" in link:
                    link = link.replace("www.np.reddit.com", "www.reddit.com")

                return link

            else:
                raise TypeError("Parameter \"link\" must be a string.")

        
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
