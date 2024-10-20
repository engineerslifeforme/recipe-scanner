# Recipes

Application for scraping and organizing recipes.

## Setup (Once) 

### Python Environment

```bash
conda create -n recipe_env python=3.11
source activate recipe_env
pip install -r requirements.txt
bash install_local_deps.sh
```

### Initialize Database

Only necessary on first execution.  Afterwards, keep database.

```bash
python db_utils.py
```

This will create `create.sql`.

Open a `sqlite3` terminal:

```bash
.open recipe.db
.read create.sql
```

## Run GUI

```bash
streamlit run app.py
```