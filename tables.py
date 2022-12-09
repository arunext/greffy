import psycopg2
from config import config
import datetime
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords

def create_tables():

    """ create tables in the PostgreSQL database"""
    params = config()
    # connect to the PostgreSQL server
    conn = psycopg2.connect(**params)

    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS POSTS
         (POST_ID INT PRIMARY KEY     NOT NULL,
          DATA           TEXT    NOT NULL,
          CREATED  TIMESTAMP NOT NULL,
          COMMENTS  INT,
          COUNT         INT);''')


    cur.execute('''CREATE TABLE IF NOT EXISTS COMMENTS
         (POST_ID INT NOT NULL,
          COMMENT_ID INT PRIMARY KEY  NOT NULL,
          DATA     TEXT    NOT NULL,
          CREATED  TIMESTAMP NOT NULL,
          UPVOTES  INT,
          DOWNVOTES INT);''')

    conn.commit()
    conn.close()

def show_table():

    print("creating tables with")
    create_tables() #creating table, later check if table exists.

    print("Inside show tables")
    """ show tables from the PostgreSQL database"""
    params = config()
    # connect to the PostgreSQL server
    conn = psycopg2.connect(**params)
    print ("Opened database successfully")

    cur = conn.cursor()

    cur.execute("SELECT POST_ID, DATA, COUNT, COMMENTS from POSTS ORDER BY COUNT DESC")
    rows = cur.fetchall()

    #table_text = ""
    #for row in rows:
     #  table_text += "Post ID = " + str(row[0])
      # table_text += "Text = " + row[1]
       #table_text += "Count = " + str(row[2]) + "\n"

    conn.close()

    return rows

def show_post(postid):
        print("Inside show post")
        """ show tables from the PostgreSQL database"""
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        print ("Opened database successfully")

        cur = conn.cursor()

        cur.execute("SELECT POST_ID, COMMENT_ID, DATA, CREATED, UPVOTES, DOWNVOTES  from COMMENTS where POST_ID = {0} ORDER BY UPVOTES DESC".format(postid));
        rows = cur.fetchall()

        conn.close()

        return rows

def create_post(postid, text):
    """ insert a new post into the vendors table """

    print("inside create post")

    # read database configuration
    params = config()
    # connect to the PostgreSQL database
    conn = psycopg2.connect(**params)

    cur = conn.cursor()

    count = 0
    comments = 0
    time = datetime.datetime.utcnow();
    cur.execute("INSERT INTO POSTS (POST_ID, DATA, CREATED, COMMENTS, COUNT) VALUES (%s, %s, %s, %s, %s)",(postid,text,time,comments,count));

    conn.commit()
    print("Records created successfully")
    conn.close()

def create_comment(postid, commentid, text):
    """ insert a new comment into the post table """

    print("inside create comments")

    # read database configuration
    params = config()
    # connect to the PostgreSQL database
    conn = psycopg2.connect(**params)

    cur = conn.cursor()

    count = 0
    time = datetime.datetime.utcnow();
    cur.execute("INSERT INTO COMMENTS (POST_ID, COMMENT_ID, DATA, CREATED, UPVOTES, DOWNVOTES) VALUES (%s, %s, %s, %s, 0, 0)",(postid,commentid,text, time));

    # Get Corresponding post
    cur.execute("SELECT POST_ID, COMMENTS from POSTS where POST_ID = {0} ORDER BY COUNT DESC".format(postid));
    rows = cur.fetchall()

    for row in rows:
        comments = row[1]
        break

    comments = comments+1

    # Update Comments count of post
    cur.execute("UPDATE POSTS set COMMENTS = {0} where POST_ID = {1}".format(comments,postid));

    conn.commit()

    print("Records created successfully")
    conn.close()

def lookup_table(text):

    """ insert a new post into the vendors table """

    print("inside lookup to tables")

    # read database configuration
    params = config()
    # connect to the PostgreSQL database
    conn = psycopg2.connect(**params)

    cur = conn.cursor()

    #initialize id and count to null values
    postid = 0
    count = 0

    #Select post
    cur.execute("SELECT POST_ID, DATA, COUNT from POSTS where DATA = '{0}' ORDER BY COUNT DESC".format(text));
    rows = cur.fetchall()

    for row in rows:
        postid = row[0]
        count = row[2]
        break

    print "Lookup operation done successfully. Id =  {0}".format(id);
    conn.close()

    return postid, count

def get_post_summary(postid):
    #currently send the top comment, latet this is the key logic to send response
    print("inside get post summary")

    # read database configuration
    params = config()
    # connect to the PostgreSQL database
    conn = psycopg2.connect(**params)

    cur = conn.cursor()

    cur.execute("SELECT POST_ID, COMMENT_ID, DATA, CREATED, UPVOTES, DOWNVOTES  from COMMENTS where POST_ID = {0} ORDER BY UPVOTES DESC".format(postid));
    rows = cur.fetchall()

    count = 0

    catcomments = ""

    for row in rows:
        count = count + 1
        if count == 1:
            topcomment = row[2]
        catcomments = catcomments + row[2]

    if count == 0:
        #no comments, ask user to comment
        topcomment = "Sorry, we don't have any comments, be the first one to comment: http://greffy.herokuapp.com/post/" + str(postid)
        polarity = 0
        subjectivity = 0
    else:
        blob = TextBlob(catcomments)
        # TODO add overall positive, neutral negative instead of polarity


        blob.sentences

        words  = b

        polarity =round(blob.sentiment.polarity,2)
        subjectivity = round(blob.sentiment.subjectivity,2)

    print(topcomment,polarity)

    return topcomment,polarity

def update_table_count(postid, count):

        """ update post with count """

        print("inside lookup to tables")

        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)

        cur = conn.cursor()

        cur.execute("UPDATE POSTS set COUNT = {0} where POST_ID = {1}".format(count,postid));
        conn.commit()

        print "Update operation done successfully for POST_ID {0} and count {1}".format(postid,count)
        conn.close()

def comment_upvote(comment_id):
    """ update post with count """

    print("inside upvote comment")

    # read database configuration
    params = config()
    # connect to the PostgreSQL database
    conn = psycopg2.connect(**params)

    cur = conn.cursor()

    # Get Corresponding comment
    cur.execute("SELECT COMMENT_ID, UPVOTES, POST_ID from COMMENTS where COMMENT_ID = {0} ORDER BY UPVOTES DESC".format(comment_id));
    rows = cur.fetchall()

    for row in rows:
        upvotes = row[1]
        break

    upvotes = upvotes+1

    # Update Comments count of post
    cur.execute("UPDATE COMMENTS set UPVOTES = {0} where COMMENT_ID = {1}".format(upvotes,comment_id));
    conn.commit()


    print ("Comment upvote completed")
    conn.close()

    #return post ID so that redirect can use it
    return (row[2])

def comment_downvote(comment_id):
        """ update comment with dwnvote """

        print("inside downvote comment")

        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)

        cur = conn.cursor()

        # Get Corresponding comment
        cur.execute("SELECT COMMENT_ID, DOWNVOTES, POST_ID from COMMENTS where COMMENT_ID = {0} ORDER BY DOWNVOTES DESC".format(comment_id));
        rows = cur.fetchall()

        for row in rows:
            downvotes = row[1]
            break

        downvotes = downvotes+1

        # Update Comments count of post
        cur.execute("UPDATE COMMENTS set DOWNVOTES = {0} where COMMENT_ID = {1}".format(downvotes,comment_id));
        conn.commit()


        print ("Comment upvote completed")
        conn.close()

        #return post ID so that redirect can use it
        return (row[2])
