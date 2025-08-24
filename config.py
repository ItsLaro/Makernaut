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
TEST_SUPPORT_ROLE_ID = int(os.getenv("TEST_SUPPORT_ROLE_ID", 0))

# Update later so the support roles and mantained from a notion doc
SUPPORT_ROLE_ID = TEST_SUPPORT_ROLE_ID
GENERAL_SUPPORT_ROLE_ID = TEST_SUPPORT_ROLE_ID
TECH_SUPPORT_ROLE_ID = TEST_SUPPORT_ROLE_ID
EVENT_SUPPORT_ROLE_ID = TEST_SUPPORT_ROLE_ID

UPE_GUILD_ID = 245393533391863808 if isProd else 1065042153836912714
TEST_GUILD_ID = 1065042153836912714