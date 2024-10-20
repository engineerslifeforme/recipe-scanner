import streamlit as st

from scraping_ui import show_scraping_ui
from recipe_entry import recipe_entry
from database import database_connect
from view_recipes import view_recipes

con = database_connect()
#con = None

st.markdown("# Recipe UI")

UI_OPTIONS = [
    "Scrape Recipe",
    "Create Recipe",
    "View Recipes",
]
ui_mode = st.sidebar.radio(
    "Mode",
    options=UI_OPTIONS,
    #index=2, # Temporary for development
)

if ui_mode == UI_OPTIONS[0]:
    show_scraping_ui(con)
elif ui_mode == UI_OPTIONS[1]:
    recipe_entry(con)
elif ui_mode == UI_OPTIONS[2]:
    view_recipes(con)
