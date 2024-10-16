from pathlib import Path
from typing import List, Optional, Literal, ClassVar

from pydantic import BaseModel, field_serializer

def get_next_id(con, table_name: str) -> int:
    current_max = con.execute(f"SELECT MAX(id) FROM {table_name}").fetchone()[0]
    # Returns None when table is empty
    if current_max is None:
        return 1
    else:
        return current_max + 1
    
def prep_sql_value(value) -> str:
    if value is None:
        return "null"
    elif type(value) == str:
        return f"'{value}'"
    elif type(value) in [int, float]:
        return str(value)
    elif type(value) == bool:
        if value:
            return "1"
        else:
            return "0"
    else:
        raise ValueError(f"Unknown type: {type(value)}")
    
def find(con, table_name: str, field_name: str, value) -> int:
    value = prep_sql_value(value)
    return con.execute(f"SELECT * FROM {table_name} WHERE {field_name}={value}").fetchone()

class DbItem(BaseModel):
    table_name: ClassVar[str] = "default"
    id: Optional[int] = None
    unique_fields: Optional[List[str]] = []
    not_real_fields: Optional[List[str]] = ["not_real_fields", "unique_fields", "table_name"]

    def add_to_db(self, con, raise_error_if_duplicate: bool = False) -> int:
        model_dump = self.model_dump()
        
        for unique_field in self.unique_fields:
            answer = find(con, self.table_name, unique_field, model_dump[unique_field])
            if answer is not None:
                if raise_error_if_duplicate:
                    raise ValueError(f"{model_dump[unique_field]} not unique")
                return answer
            
        self.id = get_next_id(con, self.table_name)
        fields = ["id"]
        values = [str(self.id)]
        for field_name, value in model_dump.items():
            if field_name in self.not_real_fields or field_name == "id":
                continue
            fields.append(field_name)
            values.append(prep_sql_value(value))
        sql = f"INSERT INTO {self.table_name} ({', '.join(fields)}) VALUES ({', '.join(values)})"
        con.execute(sql)
        con.commit()
        return self.id
    
    @classmethod
    def find_by_id(cls, con, id: int) -> "DbItem":
        return cls(**find(con, cls.table_name, "id", id))
    
    @classmethod
    def get_all(cls, con) -> list:
        return [cls(**i) for i in con.execute(f"SELECT * FROM {cls.table_name}").fetchall()]

class Ingredient(BaseModel):
    name: str
    quantity: Optional[float] = None
    unit: Optional[str] = None
    contains_milk: Optional[bool] = False
    optional: Optional[bool] = False

class DbIngredient(DbItem):
    name: str
    contains_milk: Optional[bool] = False
    table_name: ClassVar[str] = "ingredient"
    unique_fields: Optional[List[str]] = ["name"]

def get_list_where(con, table_name: str, field_name: str, value):
    sql = f"SELECT * FROM {table_name} WHERE {field_name}={prep_sql_value(value)}"
    return con.execute(sql).fetchall()

class DbIngredientToRecipe(DbItem):
    recipe_id: int
    ingredient_id: int
    quantity: Optional[float] = None
    unit: Optional[str] = None
    optional: Optional[bool] = False
    table_name: ClassVar[str] = "ingredient_to_recipe"

    @classmethod
    def get_ingredients_by_recipe(cls, con, recipe_id: int) -> list:
        ingredient_references = [DbIngredientToRecipe(**r) for r in get_list_where(con, cls.table_name, "recipe_id", recipe_id)]
        db_ingredients = [DbIngredient.find_by_id(con, ir.ingredient_id) for ir in ingredient_references]
        ingredients = []
        for ir, dbi in zip(ingredient_references, db_ingredients):
            ingredients.append(Ingredient(
                optional=ir.optional,
                **dbi.model_dump(),
            ))
        return ingredients

class Direction(BaseModel):
    order_index: int
    text: str
    image: Optional[Path] = None

    @field_serializer('image')
    def serialize_image(self, image: Path, _info):
        return str(image)

class DbDirection(DbItem, Direction):
    recipe_id: int
    table_name: ClassVar[str] = "direction"

    @classmethod
    def get_by_recipe(cls, con, recipe_id: int) -> list:
        return [Direction(**d) for d in get_list_where(con, cls.table_name, "recipe_id", recipe_id)]

class DbRecipe(DbItem):
    table_name: ClassVar[str] = "recipe"
    name: str  
    servings: int
    description: str
    image_path: Optional[str] = None
    preparation_time_minutes: Optional[int] = None
    execution_time_minutes: Optional[int] = None
    reference_url: Optional[str] = None
    unique_fields: Optional[List[str]] = ["name"]

class DbToolMap(DbItem):
    recipe_id: int
    tool_id: int
    table_name: ClassVar[str] = 'recipe_to_tool'

    @classmethod
    def get_by_recipe(cls, con, recipe_id: int) -> list:
        tool_references = [DbToolMap(**t) for t in get_list_where(con, cls.table_name, "recipe_id", recipe_id)]
        return [DbTool.find_by_id(con, tr.tool_id).name for tr in tool_references]

class DbTool(DbItem):
    name: str
    table_name: ClassVar[str] = "tool"
    unique_fields: Optional[List[str]] = ["name"]

class Recipe(BaseModel):
    name: str
    ingredients: List[Ingredient]
    servings: int
    directions: List[Direction]
    description: str
    image_path: Optional[Path] = None
    tools: List[str] = None
    preparation_time_minutes: Optional[int] = None
    execution_time_minutes: Optional[int] = None
    reference_url: Optional[str] = None

    @classmethod
    def upgrade(cls, con, recipe_db: DbRecipe) -> "Recipe":
        return Recipe(
            ingredients=DbIngredientToRecipe.get_ingredients_by_recipe(con, recipe_db.id),
            directions=DbDirection.get_by_recipe(con, recipe_db.id),
            tools=DbToolMap.get_by_recipe(con, recipe_db.id),
            **recipe_db.model_dump(),
        )

    @field_serializer('image_path')
    def serialize_image_path(self, image_path: Path, _info):
        return str(image_path)

    def add_to_db(self, con):
        recipe_id = DbRecipe(**self.model_dump()).add_to_db(con, raise_error_if_duplicate=True)
        for ingredient in self.ingredients:
            ingredient_id = DbIngredient(**ingredient.model_dump()).add_to_db(con)
            DbIngredientToRecipe(recipe_id=recipe_id, ingredient_id=ingredient_id, optional=ingredient.optional).add_to_db(con)
        for direction in self.directions:
            DbDirection(recipe_id=recipe_id, **direction.model_dump()).add_to_db(con)
        for tool in self.tools:
            tool_id = DbTool(name=tool).add_to_db(con)
            DbToolMap(recipe_id=recipe_id, tool_id=tool_id).add_to_db(con)

if __name__ == "__main__":
    import sqlite3
    con = sqlite3.connect("recipe.db")
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    con.row_factory = dict_factory
    recipe_db = DbRecipe.find_by_id(con, 1)
    Recipe.upgrade(con, recipe_db)
    print("here")
        