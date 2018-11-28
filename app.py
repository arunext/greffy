#!/usr/bin/env python

import urllib
import json
import os
#import praw
import unirest #call mashape for summarizer
import re  # reglar expresson
import psycopg2 # Postggress database
import random

from flask import Flask
from flask import request
from flask import make_response
from flask import jsonify
from flask import render_template, redirect
from textblob import TextBlob
from config import config
from tables import *

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

@app.route('/new')
def my_form():
    return render_template('my-form.html')

@app.route('/new', methods=['POST'])
def my_form_post():
    text = request.form['text']
    processUrlDB(text)
    return redirect("/")

@app.route('/')
def display_table():
    result = show_table()
    return render_template("home.html",result = result)

@app.route('/', methods=['POST'])
def home_post():
    text = request.form['text']
    processUrlDB(text)
    return redirect("/")

#post pages
@app.route('/post/<postid>')
def display_post(postid):
    #do your code here
    result = show_post(postid)
    summary = get_post_summary(postid)
    return render_template("post.html",result = result, summary = summary)

@app.route('/post/<postid>', methods=['POST'])
def post_create_comment(postid):
    text = request.form['text']
    print("Got Comment" +  text)
    create_comment (postid,random.randint(1,10000000), text)
    return redirect("/post/" + postid)

@app.route('/comments/upvote/<commentid>')
def post_upvote_comment(commentid):
    postid = comment_upvote(commentid)
    return redirect("/post/"+ str(postid))

@app.route('/comments/downvote/<commentid>')
def post_downvote_comment(commentid):
    postid = comment_downvote(commentid)
    return redirect("/post/"+ str(postid))

def processRequest(req):
    print ("started processing ...")

    if req.get("result").get("action") != "yahooWeatherForecast":
        if req.get("result").get("action") == "urlProcessRequest":
            print("URL process task")
            url = req.get("result").get("parameters").get("url")
            res = processUrlDB(url)
            print("Done processing URL in DB ")
            return res
        print ("Action not yahooWeatherForecast")
        return {}
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = makeYqlQuery(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + urllib.urlencode({'q': yql_query}) + "&format=json"
    print(yql_url)

    result = urllib.urlopen(yql_url).read()
    print("yql result: ")
    print(result)

    data = json.loads(result)
    print("data is")
    print(data)
    res = makeWebhookResult(data)
    print("The result before retur is")
    print res
    return res

def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where u='c' and woeid in (select woeid from geo.places(1) where text='" + city + "')"


def prawProcessUrl (url):

    print ("Inside Praw")
#    reddit = praw.Reddit(client_id='AvWNO2-CUuoDcA',
#                     client_secret='R67wmcaVE-D02kuUQW2sw8alCO4',
#                     password='fAT-xE3-ADt-rRa',
#                     user_agent='greffy by /u/arunext',
#                     username='arunext')

    print ("Got reddit")
#    print(reddit.user.me())
#    submission = reddit.submission(url=url)

#    for top_level_comment in submission.comments:
#        top_comment = top_level_comment.body
#        break

    print top_comment
    return top_comment

def processUrl(url):

    print("inside processUrl to process")
    print(url)
    if "reddit" in url:
        print("starting prwa")
        result =  prawProcessUrl(url)
        print("Praw complete")
        print(result)
        res = makeTextJson(result)
        print("Jsonified to:")
        print(res)
        return res
    else:
        print("Inside non-reddit, doing unirest")

        # These code snippets use an open-source library. http://unirest.io/python

        paramtopass = "{\"url\":\""+url+"\",\"text\":\"\",\"sentnum\":8}"
        #paramtopass = "{\"url\":\"http://en.wikipedia.org/wiki/Automatic_summarization\",\"text\":\"\",\"sentnum\":8}"
        print(paramtopass)
        # These code snippets use an open-source library. http://unirest.io/python
        response = unirest.post("https://textanalysis-text-summarization.p.mashape.com/text-summarizer",
          headers={
            "X-Mashape-Key": "oz0JfIM2BVmshrK6jybJa9VO9Lvkp1jVTJdjsnsqzjJv1QwnxA",
            "Content-Type": "application/json",
            "Accept": "application/json"
          },
          params=(paramtopass)
        )

        print("unirest complete")
        print(response.body)
        sentence = response.body.get("sentences")
        print(sentence)
        result = ' '.join(sentence)

        print("Result is:")
        print(result)
        res = makeTextJson(result)
        print("Jsonified to text")
        print(res)
        return res

    return res

def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
             ", the temperature is " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(speech)

    slack_message = {
        "text": speech,
        "attachments": [
            {
                "title": channel.get('title'),
                "title_link": channel.get('link'),
                "color": "#36a64f",

                "fields": [
                    {
                        "title": "Condition",
                        "value": "Temp " + condition.get('temp') +
                                 " " + units.get('temperature'),
                        "short": "false"
                    },
                    {
                        "title": "Wind",
                        "value": "Speed: " + channel.get('wind').get('speed') +
                                 ", direction: " + channel.get('wind').get('direction'),
                        "short": "true"
                    },
                    {
                        "title": "Atmosphere",
                        "value": "Humidity " + channel.get('atmosphere').get('humidity') +
                                 " pressure " + channel.get('atmosphere').get('pressure'),
                        "short": "true"
                    }
                ],

                "thumb_url": "http://l.yimg.com/a/i/us/we/52/" + condition.get('code') + ".gif"
            }
        ]
    }

    facebook_message = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [
                    {
                        "title": channel.get('title'),
                        "image_url": "http://l.yimg.com/a/i/us/we/52/" + condition.get('code') + ".gif",
                        "subtitle": speech,
                        "buttons": [
                            {
                                "type": "web_url",
                                "url": channel.get('link'),
                                "title": "View Details"
                            }
                        ]
                    }
                ]
            }
        }
    }

    print(json.dumps(slack_message))

    return {
        "speech": speech,
        "displayText": speech,
        "data": {"slack": slack_message, "facebook": facebook_message},
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


#Creating a URL in DB
def processUrlDB(url):

    postid = 0
    count = 0
    postid, count = lookup_table(url)
    print("lookup returned id= {0}, count = {1}".format(postid,count))

    if postid == 0:
        print("ID is zero, inserting")
        create_post (random.randint(1,10000000), url) #add url into table
        return makeTextJson("We haven't seen  this link before. Thanks for sharing. Start the conversation about this on: goo.gl/w8vGrv")
    else:
        print("ID is not zero, updating")
        update_table_count(postid, count+1)
        response = get_post_summary(postid)
        response =  response + " Join the discussion on greffy.herokuapp.com/post/" + str(postid)
        return makeTextJson(response)


def makeTextJson(data):

    speech = data

    print("Response:")
    print(data)

    slack_message = {
        "text": speech,
        "attachments": [
            {
                "title": speech,
                "title_link": speech,
                "color": "#36a64f",

                "fields": [
                    {
                        "title": "Condition",
                        "value": "Temp " + speech +
                                 " " + speech,
                        "short": "false"
                    },
                    {
                        "title": "Wind",
                        "value": "Speed: " + speech +
                                 ", direction: " + speech,
                        "short": "true"
                    },
                    {
                        "title": "Atmosphere",
                        "value": "Humidity " + speech +
                                 " pressure " + speech,
                        "short": "true"
                    }
                ],

                "thumb_url": "http://l.yimg.com/a/i/us/we/52/" + "abcd.gif"
            }
        ]
    }

    facebook_message = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [
                    {
                        "title": speech,
                        "image_url": "http://l.yimg.com/a/i/us/we/52/" + "abcd.gif",
                        "subtitle": speech,
                        "buttons": [
                            {
                                "type": "web_url",
                                "url": "reddit.com",
                                "title": "View Details"
                            }
                        ]
                    }
                ]
            }
        }
    }

    print(json.dumps(slack_message))

    return {
        "speech": speech,
        "displayText": speech,
        "data": {"slack": slack_message, "facebook": facebook_message},
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }

#Connect to Postgress DB. Configs in database.ini
def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

 # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)

     # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print ("Starting app on port %d" % port)
    connect()
    app.run(debug=False, port=port, host='0.0.0.0')
