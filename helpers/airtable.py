import os
import requests
import discord

AIRTABLE_API_KEY = os.environ['AIRTABLE_UPE_API_KEY']


# TODO: Organize these constants better
AIRTABLE_UPE_BASE_ID='appIYzWDeROTPg8Yv'
AIRTABLE_UPE_MEMBERSHIP_TABLE_ID='tbluUiP1zIUtP2uwS'
AIRTABLE_UPE_AA_BASE_ID='appmBfrXhvebmMnbq'
AIRTABLE_UPE_AA_MEMBERSHIP_TABLE_ID='tblGjYHulggH2gGPJ'

def get_record_by_email(email):
    '''
    Returns full response json, of all pages
    '''

    endpoint = f'https://api.airtable.com/v0/{AIRTABLE_UPE_AA_BASE_ID}/{AIRTABLE_UPE_AA_MEMBERSHIP_TABLE_ID}'
    headers = {
        'Authorization': f'Bearer {AIRTABLE_API_KEY}', 
        'Content-Type': 'application/json'
    }
    
    # Params
    ACCEPTED_VIEW = "Accepted"
    FIELDS = ["Name", "Email", "Discord ID"]
    FORMULA = f"{{Email}}='{email}'"
    params = {"view": ACCEPTED_VIEW, "fields": FIELDS, "filterByFormula": FORMULA} 

    response = requests.get(endpoint, headers=headers, params=params)
    data = response.json()
    record = data.get("records")

    return record[0] if len(record) else None

def store_token_by_record(record, token: str):
    url = f"https://api.airtable.com/v0/{AIRTABLE_UPE_AA_BASE_ID}/{AIRTABLE_UPE_AA_MEMBERSHIP_TABLE_ID}/{record['id']}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "fields": {
            "Email Token": token
        }
    }

    response = requests.patch(url, headers=headers, json=data)

    return response.status_code == 200

def verify_discord_user(record, discord_user: discord.User):
    url = f"https://api.airtable.com/v0/{AIRTABLE_UPE_AA_BASE_ID}/{AIRTABLE_UPE_AA_MEMBERSHIP_TABLE_ID}/{record['id']}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "fields": {
            "Email Token": '',
            "Discord ID": discord_user.id,
            "Discord Username": str(discord_user),
        }
    }

    response = requests.patch(url, headers=headers, json=data)

    return response.status_code == 200