import os
import sqlite3


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def db_init():
    con = sqlite3.connect(BASE_DIR+'/robotsdna.db')
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS persons (slug text,name text)')
    con.close()


def db_insert(slug, name):
    con = sqlite3.connect(BASE_DIR+'/robotsdna.db')
    cur = con.cursor()
    record = cur.execute("INSERT INTO persons VALUES ('" + slug + "', '" + name + "')")
    con.commit()
    con.close()
    return record


def db_clear():
    con = sqlite3.connect(BASE_DIR+'/robotsdna.db')
    cur = con.cursor()
    cur.execute("DELETE FROM persons")
    con.commit()
    con.close()


def db_select(slug):
    con = sqlite3.connect(BASE_DIR+'/robotsdna.db')
    cur = con.cursor()
    cur.execute('SELECT name FROM persons  where slug="' + slug + '"')
    row = cur.fetchone()
    con.close()
    return row
