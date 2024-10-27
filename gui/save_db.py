""" Save DB to server """

from datetime import date
from pathlib import Path
import shutil
import sys
import filecmp

action = sys.argv[1]

SERVER = Path('/Volumes/Media/recipe_db')
SERVER_IMAGES = SERVER / "images"
SERVER_RECIPES = SERVER / "recipes"
ASSETS = SERVER / 'assets'
LOCAL_FILE = Path('recipe.db')

if action in ['upload', 'upload_db']:
    print('Uploading...')
    date_str = date.today().strftime("%Y%m%d")
    new_file = SERVER / f'{date_str}.db'
    print(f'Saving file to {new_file}')
    shutil.copyfile(LOCAL_FILE, new_file)
    for image in (LOCAL_FILE.parent / "images").glob("*"):
        destination = SERVER_IMAGES / image.name
        if not destination.exists():
            shutil.copyfile(image, destination)
    for recipe in (LOCAL_FILE.parent / "recipes").glob("*"):
        destination = SERVER_IMAGES / recipe.name
        if not destination.exists():
            shutil.copyfile(recipe, destination)

elif action in ['download', 'download_db']:
    print('Downloading...')
    server_file_list = list(SERVER.glob('*.db'))
    server_file_list.sort()
    server_file = server_file_list[-1]
    print(f'Copying {server_file}')
    shutil.copyfile(server_file, LOCAL_FILE)
    for image in SERVER_IMAGES.glob("*"):
        destination = LOCAL_FILE.parent / "images" / image.name
        if not destination.exists():
            shutil.copyfile(image, destination)
    for recipe in SERVER_RECIPES.glob("*"):
        destination = LOCAL_FILE.parent / "recipes" / recipe.name
        if not destination.exists():
            shutil.copyfile(recipe, destination)
    
else:
    print(f'Unknown command {action}')