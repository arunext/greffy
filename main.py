import random, string
import os
from flask import Flask, render_template, request

#Summarizer
import requests
from bs4 import BeautifulSoup
#https://towardsdatascience.com/scrape-and-summarize-news-articles-in-5-lines-of-python-code-175f0e5c7dfc
from newspaper import Article
import nltk

#For twitter CRC
import base64
import hashlib
import hmac
import json

nltk.download('punkt')

#Import other files in the project
from twitter import *

app = Flask(  # Create a flask app
  __name__,
  template_folder='templates',  # Name of html file folder
  static_folder='static'  # Name of directory for static files
)

ok_chars = string.ascii_letters + string.digits


@app.route('/')
def display_home():
  return render_template("home.html",
                         title="Tools to deepdive into the internet")


@app.route('/sharepost')
def display_newpost():
  res = "hello"
  title = "Create and share quick notes"
  return render_template("sharepost.html",
                         res="",
                         title="Create and share quick notes")


@app.route('/2')
def page_2():
  rand_ammnt = random.randint(10, 100)
  random_str = ''.join(random.choice(ok_chars) for a in range(rand_ammnt))
  return render_template('site_2.html', random_str=random_str)


@app.route('/summarize-url')
def display_url_summary():
  return render_template("url.html", res="", title="Summarize a URL")


@app.route('/summarize-url', methods=['POST'])
def home_post_url():

  url = request.form['text']
  #page = requests.get(url)
  #soup = BeautifulSoup(page.content, 'html.parser')

  #content = soup.get_text()

  #summary = summarize(content, 0.05)

  summary = summarizeurl(url)

  return render_template("url.html", res=summary, title="Summarize a URL")


@app.route('/twittermention', methods=['GET'])
def twitter_mention():
  #Webhook triggered from IFTTT hello@greffy.com when bot is metioned and 15 mins
  #API below will take care of responses

  #NOTE: Apparently the Account Acitivity was removed from non premium users on 16 Aug 2022 :(. So probably IFTTT won't work either.

  print("received twitter webhook")

  respondToTweet()

  return render_template("home.html", res="", title="Get top tweets")


@app.route('/twitter')
def display_twitter():
  return render_template("twitter.html", res="", title="Get top tweets")


@app.route('/twitter', methods=['POST'])
def post_twitter():
  text = request.form['text']
  sentence = searchTweet(text)

  return render_template("twitter.html", res=sentence, title="Get top tweets")


@app.route('/summarize-text')
def display_table():
  return render_template("summary.html",
                         res="You'll get the summary here",
                         title="Summarize Text")


@app.route('/summarize-text', methods=['POST'])
def home_post():
  text = request.form['text']
  res = summarize(text)
  #res = processUrl(text)
  print(res)
  #return redirect("/")
  return render_template("summary.html", res=res, title="Summarize Text")


#Old static pages with some remnant Seo
@app.route('/coffee-pods-sustainable-alternative/')
def coffee():
  return render_template("coffee-pods-sustainable-alternative.html")


@app.route('/efficient-kitchen-tools')
def kitchen():
  return render_template("efficient-kitchen-tools.html")


@app.route('/clever-hiking-gear-outdoor-cheap')
def hiking():
  return render_template("clever-hiking-gear-outdoor-cheap.html")


def summarizeurl(url):

  try:
    urlcontent = Article(url)
    urlcontent.download()
    urlcontent.parse()
    urlcontent.nlp()

    summary = urlcontent.summary

  except:
    return "Sorry, could not extract content."

  return summary


if __name__ == "__main__":  # Makes sure this is the main process
  app.run(  # Starts the site
    host='0.0.0.0',  # EStablishes the host, required for repl to detect the site
    port=random.randint(2000,
                        9000)  # Randomly select the port the machine hosts on.
  )
