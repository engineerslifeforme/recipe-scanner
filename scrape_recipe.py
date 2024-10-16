from pathlib import Path
import re
#import urllib
import urllib.request

from bs4 import BeautifulSoup
import yaml

from models import Recipe, Direction, Ingredient


IMAGE_PATH = Path("images")
IMAGE_PATH.mkdir(exist_ok=True)
RECIPE_PATH = Path("recipes")
RECIPE_PATH.mkdir(exist_ok=True)

def parse_quantity(input: str) -> float:
    if input == "¼":
        output = 0.75
    else:
        output = float(input)
    return output

def get_index(text: str) -> tuple:
    end = 1
    for _ in range(len(text)):
        try:
            index = int(text[0:end])
        except ValueError:
            break
        end += 1
    return index, end - 1

def scrape_directions(soup, title: str) -> list:
    raw_directions = soup.findAll("div", {"data-test-id" : "instruction-step"})
    directions = []
    for direction in raw_directions:
        content = direction.text
        index, character_length = get_index(content)
        text = content[character_length:].replace("\n", " ")
        directions.append(Direction(
            order_index=index,
            text=text,
            image=Path("..") / get_image(direction.find_all("img")[0], f"{index}-{title}")
        ))
    return directions

def scrape_ingredients(soup) -> list:
    ingredients = soup.findAll("div", {"data-test-id" : "ingredient-item-shipped"})
    ingredients += soup.findAll("div", {"data-test-id" : "ingredient-item-not-shipped"})
    ingredient_list = list()
    for ingredient in ingredients:
        contains_milk = False
        units_item = list(ingredient.children)[1]
        units_item_children = list(units_item.children)
        try:
            quantity, units = units_item_children[0].text.split(" ")
            quantity = parse_quantity(quantity)
        except ValueError:
            # No quantity provided
            quantity = None
            units = None
        item = units_item_children[1]
        ingredient_unit = None
        if units != "unit":
            ingredient_unit = units
        if len(units_item_children) > 2:
            if "Contains  Milk" in units_item_children[2].text:
                contains_milk = True
        ingredient_list.append(Ingredient(
            name=item.text,
            quantity=quantity,
            unit=ingredient_unit,
            contains_milk=contains_milk,
        ))
    return ingredient_list

def get_title(soup) -> str:
    primary_title = soup.find_all("h1")[0].text
    secondary_title = soup.find_all("h2")[0].text
    return f"{primary_title} {secondary_title}"

def clean_description(soup) -> str:
    return list(soup.children)[0].text

def extract_ints(text: str) -> list:
    ints = [int(i) for i in re.findall(r'\d+', text)]
    assert(len(ints) > 0)
    return ints

def get_times(soup) -> tuple:
    total_time = None
    execution_time = None
    preparation_time = None
    for entry in soup.children:
        entry_text = entry.text
        if "Total Time" in entry_text:
            try:
                total_time = extract_ints(entry_text)[0]
            except AssertionError:
                pass
        elif "Prep Time" in entry_text:
            try:
                preparation_time = extract_ints(entry_text)[0]
            except AssertionError:
                pass
    if total_time is not None and preparation_time is not None:
        execution_time = total_time - preparation_time
    elif total_time is not None:
        execution_time = total_time
    return (preparation_time, execution_time)

def get_description(soup) -> tuple:
    recipe_description = soup.findAll("div", {"data-test-id" : "recipe-description"})[0]
    description_blocks = list(recipe_description.children)
    sub_blocks = list(description_blocks[1].children)
    description = clean_description(sub_blocks[0])
    title = get_title(description_blocks[0])
    times = get_times(sub_blocks[1])
    return (description, title, times)

def get_tools(soup) -> list:
    # utensils-list-item
    utensils = soup.findAll("div", {"data-test-id" : "utensils-list-item"})
    return [d.text for d in utensils]

def get_image(img_element, name: str) -> Path:
    image_src = img_element.attrs["src"]
    extension = image_src.split(".")[-1]
    destination = IMAGE_PATH / f"{name}.{extension}"
    if not destination.exists():
        urllib.request.urlretrieve(image_src, destination)
    return destination

def get_recipe_image(soup, title: str) -> Path:
    image_div = soup.findAll("div", {"data-test-id" : "recipe-hero-image"})[0]
    return get_image(image_div.find("img"), title)

def scrape_recipe(html_text: str) -> Path:
    soup = BeautifulSoup(html_text, "html.parser")
    ingredient_list = scrape_ingredients(soup)
    description, title, times = get_description(soup)
    direction_list = scrape_directions(soup, title)
    
    recipe_data = Recipe(
        ingredients=ingredient_list,
        directions=direction_list,
        name=title,
        servings=2,
        preparation_time_minutes=times[0],
        execution_time_minutes=times[1],
        description=description,
        tools=get_tools(soup),
        image_path=Path("..") / get_recipe_image(soup, title),
    ).model_dump()
    recipe_data["image_path"] = str(recipe_data["image_path"])
    for direction in recipe_data["directions"]:
        direction["image"] = str(direction["image"])
    destination = RECIPE_PATH / f"{title}.yaml"
    destination.write_text(yaml.safe_dump(recipe_data))
    return destination

if __name__ == "__main__":
    recipe_path = scrape_recipe(Path("recipe.html").read_text())
    recipe = Recipe(**yaml.safe_load(recipe_path.read_text()))
    import sqlite3
    con = sqlite3.connect("recipe.db")
    recipe.add_to_db(con)