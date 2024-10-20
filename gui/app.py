import streamlit as st

from scraping_ui import show_scraping_ui
from recipe_entry import recipe_entry
from database import database_connect

con = database_connect()

st.markdown("# Recipe UI")

UI_OPTIONS = [
    "Scrape Recipe",
    "Create Recipe",
]
ui_mode = st.sidebar.radio(
    "Mode",
    options=UI_OPTIONS,
)

if ui_mode == UI_OPTIONS[0]:
    show_scraping_ui(con)

elif ui_mode == UI_OPTIONS[1]:
    recipe_entry(con)