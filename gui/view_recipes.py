import streamlit as st
import pandas as pd

from recipe_api.models import (
    DbRecipe,
    DbIngredientToRecipe,
)

def view_recipes(con):
    st.markdown("## View Recipes")
    db_recipes = DbRecipe.get_all(con)
    st.markdown(f"{len(db_recipes)} Recipes in database")
    st.write(pd.DataFrame([{"name": r.name, "id": r.id} for r in db_recipes]))
    selected_db_recipes = st.multiselect(
        "Selected Recipes",
        options=db_recipes,
        format_func= lambda x: x.name,
    )
    st.markdown("### Ingredient List")
    ingredients = []
    for db_recipe in selected_db_recipes:
        ingredients.extend(DbIngredientToRecipe.get_ingredients_by_recipe(con, db_recipe.id))
    st.write(pd.DataFrame([{"name": i.name, "quantity": i.quantity, "unit": i.unit} for i in ingredients]))
    ingredient_strs = []
    for ingredient in ingredients:
        parts = ["\n- ", ingredient.name]
        if ingredient.quantity is not None:
            parts.append(str(ingredient.quantity))
        if ingredient.unit is not None:
            parts.append(str(ingredient.unit))
        ingredient_strs.append(" ".join(parts))
    st.markdown("".join(ingredient_strs))