import os
import requests
import discord

# TODO: Organize these constants better
AIRTABLE_INIT_PRO_BASE_ID='appLZ8fe3NAkBqvhY'
AIRTABLE_INIT_PRO_MEMBERSHIP_TABLE_ID='tbluGowfHrBkfpNdP'

def get_record_by_email(email):
    AIRTABLE_API_KEY = os.environ['AIRTABLE_API_KEY']

    endpoint = f'https://api.airtable.com/v0/{AIRTABLE_INIT_PRO_BASE_ID}/{AIRTABLE_INIT_PRO_MEMBERSHIP_TABLE_ID}'

    headers = {
        'Authorization': f'Bearer {AIRTABLE_API_KEY}', 
    }
    
    # Params
    ACCEPTED_VIEW = "viwu6rzpHULfuCvLo"
    FIELDS = ["First Name", "E-mail Address", "Discord ID"]
    FORMULA = f"{{E-mail Address}}='{email}'"
    params = {"view": ACCEPTED_VIEW, "fields": FIELDS, "filterByFormula": FORMULA} 

    response = requests.get(endpoint, headers=headers, params=params)
    data = response.json()
    record = data.get("records")

    return record[0] if len(record) else None

def store_token_by_record(record, token: str):
    AIRTABLE_API_KEY = os.environ['AIRTABLE_API_KEY']

    url = f"https://api.airtable.com/v0/{AIRTABLE_INIT_PRO_BASE_ID}/{AIRTABLE_INIT_PRO_MEMBERSHIP_TABLE_ID}/{record['id']}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    }
    data = {
        "fields": {
            "Discord Email Token": token
        }
    }

    response = requests.patch(url, headers=headers, json=data)

    return response.status_code == 200

def verify_discord_user(record, discord_user: discord.User):
    AIRTABLE_API_KEY = os.environ['AIRTABLE_API_KEY']
    
    url = f"https://api.airtable.com/v0/{AIRTABLE_INIT_PRO_BASE_ID}/{AIRTABLE_INIT_PRO_MEMBERSHIP_TABLE_ID}/{record['id']}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "fields": {
            "Discord Email Token": '',
            "Discord ID": discord_user.id,
            "Discord Username": str(discord_user),
        }
    }

    response = requests.patch(url, headers=headers, json=data)
    print(response.status_code, response.reason, response.text)

    return response.status_code == 200