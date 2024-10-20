from typing import Optional
from pathlib import Path

from recipe_api.models import (
    DbDirection,
    DbIngredient,
    DbIngredientToRecipe,
    DbRecipe,
    DbTool,
    DbToolMap,
)

MODELS = [
    DbDirection,
    DbIngredient,
    DbIngredientToRecipe,
    DbRecipe,
    DbTool,
    DbToolMap,
]

SQL_TYPE_MAP = {
    str: "TEXT",
    int: "INTEGER",
    Path: "TEXT",
    float: "REAL",
    bool: "BOOLEAN",
}
SQL_TYPE_MAP.update({Optional[k]: v for k, v in SQL_TYPE_MAP.items()})

def generate_create_statements() -> list:
    statements = []
    for model in MODELS:
        fields_and_types = []
        for field_name, field_info in model.model_fields.items():
            if field_name in model.model_fields["not_real_fields"].default:
                continue
            field_type = SQL_TYPE_MAP[field_info.annotation]
            fields_and_types.append(f"{field_name} {field_type}")
        create_statement = f"CREATE TABLE {model.table_name} ({', '.join(fields_and_types)});"
        print(create_statement)
        statements.append(create_statement)
    return statements

if __name__ == "__main__":
    create_path = Path("create.sql")
    statements = generate_create_statements()
    create_path.write_text("\n".join(statements))