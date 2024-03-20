from dotenv import load_dotenv
load_dotenv()

import os

TOKEN = os.getenv('TOKEN')
JSON_PATH = os.getenv('JSON_PATH')
INTERVAL_SEC = int(os.getenv('INTERVAL_SEC'))
GHOST_LIMIT = int(os.getenv('GHOST_LIMIT'))
ROLE_NAME = os.getenv('ROLE_NAME')