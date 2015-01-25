from __future__ import print_function
import mechanize
import os
import praw
from praw.errors import *
import re
from requests.exceptions import HTTPError
from socket import *
import sqlite3 as db
from simpleconfigparser import simpleconfigparser
from sys import exit
from time import sleep


config = simpleconfigparser()

if not(os.path.isfile("settings.cfg")):
print("Couldn't find settings.cfg. Exiting.")
exit(1)
else:
config.read("settings.cfg")

con = db.connect("alreadyarchived.db")
cur = con.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS submissions(permalink TEXT)")

archive_submitter = mechanize.Browser()

client = praw.Reddit(user_agent="/u/PopcornArchiver Bot by /u/SirNeon")

USERNAME = str(config.login.username)
PASSWORD = str(config.login.password)
SUBMISSION_LIMIT = int(config.main.max_submissions)
SUBREDDIT_LIST = list(set(str(config.main.subreddit_list).split(',')))


def login(username, password):
print("Logging in as {}...".format(username))

while True:
    try:
        client.login(username, password)
        break
    except (HTTPError, timeout) as e:
        print(e)
        continue
    except (InvalidUser, InvalidUserPass, RateLimitExceeded, APIException) as e:
        print(e)
        exit(1)


def get_submissions(multireddit):
while True:
    try:
        submissions = client.get_subreddit(multireddit).get_new(limit=SUBMISSION_LIMIT)
        break
    except (HTTPError, timeout) as e:
        continue

return submissions


def get_reddit_urls(submission):
# matches reddit submissions, but not just
# https://www.reddit.com/r/SomeSubreddit
reddit_url_pattern = re.compile("https?\:\/\/[\w.]+reddit\.com\/r\/[\w\d]+\/[\w\d/]+")

if(submission.is_self):
    reddit_urls = reddit_url_pattern.findall(str(submission.selftext))
    if(reddit_urls != []):
        return reddit_urls
    else:
        return None
else:
    reddit_url = reddit_url_pattern.match(str(submission.url))
    if reddit_url is not None:
        return [reddit_url.group(0)]
    else:
        return None


def get_archive_today(link):
while True:
    try:
        archive_submitter.open("http://archive.today")
        archive_submitter.select_form(nr=0)
        archive_submitter["url"] = link
        archive_submitter.submit()
        
        # this is necessary to get the actual archive url instead of
        # http://archive.today/submit
        response = archive_submitter.reload()
        break
    except Exception:
        continue

return response.geturl()


def format_comment(source_archive_dict):
comment_body = ""

for source, archive in source_archive_dict.iteritems():
    comment_body += "[[source]]({}) ".format(source)
    comment_body += "[[archive.today]]({})\n\n".format(archive[0])

comment_body += "\n---\n[Open Source]({}) |".format("https://github.com/SirNeon618/PopcornArchiver")
comment_body += " [Feedback]({})\n".format("https://www.reddit.com/message/compose?to=%2Fr%2FPopcornArchiver")

return comment_body


def submit_comment(submission, text):
while True:
    try:
        submission.add_comment(text)
        break
    except (HTTPError, timeout) as e:
        continue


def main():
login(USERNAME, PASSWORD)
multireddit = ""

for subreddit in SUBREDDIT_LIST:
    multireddit += subreddit + '+'

multireddit = multireddit.strip('+')

while True:
    submissions = get_submissions(multireddit)

    for submission in submissions:
        permalink = str(submission.permalink)
        cur.execute("SELECT permalink FROM submissions WHERE permalink=?", (permalink,))
        
        if(cur.fetchone() != None):
            continue

        archived_links = {}
        links = get_reddit_urls(submission)

        if links is not None:
            for link in links:
                archive_today = get_archive_today(link)
                # uses a list in case multiple archive services are desireable.
                archived_links[link] = [archive_today]

            text = format_comment(archived_links)
            submit_comment(submission, text)

        cur.execute("INSERT INTO submissions VALUES(?)", (permalink,))
        con.commit()

        sleep(60)


if __name__ == "__main__":
main()
