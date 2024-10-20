import streamlit as st

from recipe_api.models import Recipe, DbIngredient

def recipe_entry(con):
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