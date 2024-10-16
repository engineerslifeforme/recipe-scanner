import requests

import streamlit as st
import yaml
import sqlite3

from scrape_recipe import scrape_recipe
from models import Recipe, DbIngredient

con = sqlite3.connect("recipe.db")

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
con.row_factory = dict_factory

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
    st.markdown("## Scrape Recipe")
    recipe_url = st.text_input("Recipe URL")
    if st.button("Scrape Recipe"):
        recipe_yaml_path = scrape_recipe(requests.get(recipe_url).text)
        recipe = Recipe(**yaml.safe_load(recipe_yaml_path.read_text()))
        st.markdown(recipe.name)

elif ui_mode == UI_OPTIONS[1]:
    st.markdown("## Create Recipe")
    title = st.text_input("Recipe Title")
    ingredient_quantity = st.sidebar.number_input(
        "Ingredient Quantity",
        value = 1,
        step = 1,
        min_value=1,
    )
    recipe_step_quantity = st.sidebar.number_input(
        "Recipe Step Quantity",
        value = 1,
        step = 1,
        min_value=1,
    )
    with st.expander("Ingredient Details", expanded=True):
        for index in range(ingredient_quantity):
            db_ingredients = DbIngredient.get_all(con)
            selected_ingredient = st.selectbox(
                f"Ingredient #{index+1}",
                options=db_ingredients,
                format_func=lambda x : x.name,
            )
    with st.expander("Step Details", expanded=True):
        for index in range(recipe_step_quantity):
            step_content = st.text_area(f"Step #{index+1}")