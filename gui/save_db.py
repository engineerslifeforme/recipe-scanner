""" Save DB to server """

from datetime import date
from pathlib import Path
import shutil
import sys
import filecmp

action = sys.argv[1]

SERVER = Path('/Volumes/Media/recipe_db')
ASSETS = SERVER / 'assets'
LOCAL_FILE = 'recipe.db'

if action in ['upload', 'upload_db']:
    print('Uploading...')
    date_str = date.today().strftime("%Y%m%d")
    new_file = SERVER / f'{date_str}.db'
    print(f'Saving file to {new_file}')
    shutil.copyfile(LOCAL_FILE, new_file)

elif action in ['download', 'download_db']:
    print('Downloading...')
    server_file_list = list(SERVER.glob('*.db'))
    server_file_list.sort()
    server_file = server_file_list[-1]
    print(f'Copying {server_file}')
    shutil.copyfile(server_file, LOCAL_FILE)
    
else:
    print(f'Unknown command {action}')