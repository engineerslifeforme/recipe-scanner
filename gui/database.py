from pathlib import Path
import sqlite3

from recipe_api.db_utils import generate_create_statements

RECIPE_DB_PATH = Path("recipe.db")

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def initialize(con):
    initialization_statements = generate_create_statements()
    for statement in initialization_statements:
        con.execute(statement)
    con.commit()

def database_connect():
    initialize_needed = False
    if not RECIPE_DB_PATH.exists():
        initialize_needed = True
    con = sqlite3.connect("recipe.db")
    con.row_factory = dict_factory
    if initialize_needed:
        initialize(con)
    return con
