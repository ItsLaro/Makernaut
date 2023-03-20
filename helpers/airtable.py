import os

AIRTABLE_API_KEY = os.environ['AIRTABLE_UPE_API_KEY']

def get_all_records(base_id, table_id):
    '''
    Returns full response json, of all pages
    '''

    all_records = []
    endpoint = f'https://api.airtable.com/v0/{base_id}/{table_id}'
    headers = {
        'Authorization': f'Bearer {AIRTABLE_API_KEY}', 
        'Content-Type': 'application/json'
    }
    url = endpoint
    while True:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            records = data['records']
            all_records.extend(records)
            if 'offset' in data:
                url = endpoint + '?offset=' + data['offset']
            else:
                break
        except Exception as e:
            print(f'Something went wrong with the airtable query: {e}')
            break
    
    return all_records

def get_record_by_email(records, email):
    for record in records:
        record_email = record['fields']['E-Mail Address']
        if email.strip() == record_email:   
            return record
    return None
           