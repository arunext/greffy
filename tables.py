import psycopg2
from config import config

def create_tables():

    print("Inside create tables")
    """ create tables in the PostgreSQL database"""
    params = config()
    # connect to the PostgreSQL server
    conn = psycopg2.connect(**params)
    print ("Opened database successfully")

    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS POSTS
         (ID INT PRIMARY KEY     NOT NULL,
          DATA           TEXT    NOT NULL,
          COUNT         INT);''')
    print ("Table created successfully")

    conn.commit()
    conn.close()

def show_table():

    print("Inside show tables")
    """ show tables from the PostgreSQL database"""
    params = config()
    # connect to the PostgreSQL server
    conn = psycopg2.connect(**params)
    print ("Opened database successfully")

    cur = conn.cursor()

    cur.execute("SELECT ID, DATA, COUNT from POSTS ORDER BY COUNT DESC")
    rows = cur.fetchall()

    #table_text = ""
    #for row in rows:
     #  table_text += "Post ID = " + str(row[0])
      # table_text += "Text = " + row[1]
       #table_text += "Count = " + str(row[2]) + "\n"

    conn.close()
    return rows

def insert_tables(postid, text):
    """ insert a new post into the vendors table """

    print("inside insert to tables")

    # read database configuration
    params = config()
    # connect to the PostgreSQL database
    conn = psycopg2.connect(**params)

    cur = conn.cursor()

    count = 0
    cur.execute("INSERT INTO POSTS (ID,DATA,COUNT) VALUES (%s, %s, %s)",(postid,text,count));

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
    id = 0
    count = 0

    #Select post
    cur.execute("SELECT ID, DATA, COUNT from POSTS where DATA = '{0}' ORDER BY COUNT DESC".format(text));
    rows = cur.fetchall()

    for row in rows:
        id = row[0]
        count = row[2]
        break

    print "Lookup operation done successfully. Id =  {0}".format(id);
    conn.close()

    return id, count

def update_table(id, count):

        """ update post with count """

        print("inside lookup to tables")

        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)

        cur = conn.cursor()

        cur.execute("UPDATE POSTS set COUNT = {0} where ID = {1}".format(count,id));
        conn.commit()
        print "Total number of rows updated :", cur.rowcount

        print "Update operation done successfully for id {0} and count {1}".format(id,count);
        conn.close()
