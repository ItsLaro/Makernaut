import argparse
import os
from dotenv import load_dotenv
load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--isProd", help="Production Mode", action='store_true')
args = parser.parse_args()

isProd = args.isProd

# Load Variables
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_KB_DATABASE_ID = os.getenv("NOTION_KB_DATABASE_ID")
NOTION_SUPPORT_DATABASE_ID = os.getenv("NOTION_SUPPORT_DATABASE_ID")
TEST_SUPPORT_ROLE_ID = int(os.getenv("TEST_SUPPORT_ROLE_ID", 0))

# Update later so the support roles and mantained from a notion doc
SUPPORT_ROLE_ID = TEST_SUPPORT_ROLE_ID
GENERAL_SUPPORT_ROLE_ID = TEST_SUPPORT_ROLE_ID
TECH_SUPPORT_ROLE_ID = TEST_SUPPORT_ROLE_ID
EVENT_SUPPORT_ROLE_ID = TEST_SUPPORT_ROLE_ID

# Guild IDs
UPE_GUILD_ID = int(os.getenv("PROD_GUILD_ID")) if isProd else int(os.getenv("TEST_GUILD_ID"))
TEST_GUILD_ID = int(os.getenv("TEST_GUILD_ID"))