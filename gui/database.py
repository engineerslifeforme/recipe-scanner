import sqlite3

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def database_connect():
    con = sqlite3.connect("recipe.db")
    con.row_factory = dict_factory
    return con
