import tweepy
from textblob import TextBlob
import urllib
#Following needs to be pip installed from shell
import validators
import re

from main import *

#For twitter bot from https://auth0.com/blog/how-to-make-a-twitter-bot-in-python-using-tweepy/
import json
import requests
import logging

auth = tweepy.OAuthHandler(os.environ['TWITTER_CONSUMER_KEY'],
                           os.environ['TWITTER_CONSUMER_SECRET'])
auth.set_access_token(os.environ['TWITTER_ACCESS_KEY'],
                      os.environ['TWITTER_ACCESS_SECRET'])
api = tweepy.API(auth)


def searchTweet(query):
  from bs4 import BeautifulSoup
  from html import unescape

  auth = tweepy.OAuthHandler(
    os.environ['TWITTER_CONSUMER_KEY'],
    os.environ['TWITTER_CONSUMER_SECRET'])
  auth.set_access_token(os.environ['TWITTER_ACCESS_KEY'],
                        os.environ['TWITTER_ACCESS_SECRET'])

  api = tweepy.API(auth)

  #Check if query is a URL. If so, get the title and search for it
  if validators.url(query) == True:
    webpage = urllib.request.urlopen(query).read()
    query = str(webpage).split('<title>')[1].split('</title>')[0]

  print(query)

  statuses = [
    status for status in tweepy.Cursor(
      api.search_tweets, q=query, result_type='mixed',
      tweet_mode='extended').items(100)
  ]

  responseArray = []

  for status in statuses:
    blob = TextBlob(status.full_text)
    if (blob.sentiment.subjectivity <= 0.3):
      responseArray.append([
        status.user.screen_name, status.full_text,
        round(blob.sentiment.polarity, 2),
        round(blob.sentiment.subjectivity, 2)
      ])

  responseArray.sort(key=lambda x: abs(x[3]), reverse=True)

  return responseArray


def get_last_tweet(file):
  f = open(file, 'r')
  lastId = int(f.read().strip())
  f.close()
  return lastId


def put_last_tweet(file, Id):
  f = open(file, 'w')
  f.write(str(Id))
  f.close()
  print("Updated the file with the latest tweet Id")
  return


def respondToTweet(file='tweet_ID.txt'):
  last_id = get_last_tweet(file)
  mentions = api.mentions_timeline(since_id=last_id)

  print("noone mentioned me...")

  if len(mentions) == 0:
    return

  new_id = 0
  print("someone mentioned me...")

  for mention in reversed(mentions):
    print(str(mention.id) + '-' + mention.text)
    new_id = mention.id

    url = mention.entities['urls'][0]['expanded_url']
    valid = validators.url(url)

    print(url)

    #If URL, get a summary.
    if valid == True:
      response = summarizeurl(url)
    else:
      response = "Sorry, not a URL"

    print(response)

    # Split the text into 280-character chunks
    chunks = [response[i:i + 280] for i in range(0, len(response), 280)]

    try:
      api.create_favorite(mention.id_str)
      reply_to_id = mention.id_str
      for chunk in chunks:
        print("Updating status in reply to" + reply_to_id)
        newstatus = api.Client.create_tweet(
          text='@' + mention.user.screen_name + " " + chunk,
          in_reply_to_status_id=reply_to_id)
        #Have the chunks in the same thread.
        reply_to_id = newstatus.id_str
    except:
      print("Error in replying to {}".format(mention.id_str))

  put_last_tweet(file, new_id)
  return
