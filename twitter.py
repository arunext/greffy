import tweepy
from textblob import TextBlob
import urllib
#Following needs to be pip installed from shell
import validators
import re
import os

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

  auth = tweepy.OAuthHandler(os.environ['TWITTER_CONSUMER_KEY'],
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

  print("Checking mentions")

  if len(mentions) == 0:
    return

  new_id = 0

  print("Yes, there seems to be one")

  for mention in reversed(mentions):
    print(str(mention.id) + '-' + mention.text)
    new_id = mention.id

    valid = False

    #Initialized response to default response.
    response = "Sorry, tweet or parent tweet doesn't contain a URL. @ me with a URL or in response to a tweet with a URL to get a summary of the content."

    if "url" in mention.entities:
      url = mention.entities['urls'][0]['expanded_url']
      valid = validators.url(url)

    #If there is URL in the tweet, get a summary of the content within the URL.
    if valid == True:
      response = summarizeurl(url)
    else:
      print("Checking Original tweet)")
      print(mention.in_reply_to_status_id_str)
      if mention.in_reply_to_status_id_str:
        #If this tweet is in reply to a tweet, check if the Original tweet has a URL
        parenttweet = api.get_status(mention.in_reply_to_status_id_str)
        url = parenttweet.entities['urls'][0]['expanded_url']
        valid = validators.url(url)
        if valid == True:
          #Parent tweet has a URL, summarize it.
          response = summarizeurl(url)

    response = status = '@' + mention.user.screen_name + " " + response

    #Breakdown blob into sentences.
    blob = TextBlob(response)

    try:
      #Like the tweet
      api.create_favorite(mention.id_str)
      reply_to_id = mention.id_str
      for sentence in blob.sentences:
        newstatus = api.update_status(sentence[:279],
                                      in_reply_to_status_id=reply_to_id)
        #Have the chunks in the same thread.
        reply_to_id = newstatus.id_str
    except tweepy.errors.TweepyException as e:
      print(e)

  put_last_tweet(file, new_id)
  return
