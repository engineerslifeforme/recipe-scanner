import requests

import streamlit as st
import yaml

from recipe_scraper.scrape_recipe import scrape_recipe_from_url
from recipe_api.models import Recipe

def show_scraping_ui(con):
    st.markdown("## Scrape Recipe")
    recipe_url = st.text_input("Recipe URL")
    if st.button("Scrape Recipe"):
        recipe_yaml_path = scrape_recipe_from_url(recipe_url)
        recipe = Recipe(**yaml.safe_load(recipe_yaml_path.read_text()))
        st.markdown(recipe.name)
        recipe_id = recipe.add_to_db(con)
        st.success(f"Added Recipe ID: {recipe_id}")