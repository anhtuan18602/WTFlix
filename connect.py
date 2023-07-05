#!/usr/bin/python
#import psycopg2
import sqlite3
def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        # connect to the PostgreSQL server
        print('Connecting to the SQLite database...')
        conn = sqlite3.connect('movies.db')
        #conn = psycopg2.connect(**st.secrets["postgresql"])

        # create a cursor
        cur = conn.cursor()

	# execute a statement
        print('SQLite database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)

        # close the cursor
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        # return the connection
        return conn
