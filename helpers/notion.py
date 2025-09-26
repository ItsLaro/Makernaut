import os
import re
from datetime import datetime, timedelta
from notion_client import Client
import pytz
from .notion_properties import extract_property_value

class NotionDB:

    def __init__(self):
        
        env_key = os.environ['NOTION_ANC_CLIENT_ID']

        self.notion = Client(auth = env_key)
        self.faq_db_id = "2649f4e8-ae4e-802e-b6dc-e54e30078892"
        self.anc_db_id = "2649f4e8-ae4e-8060-8768-c397e8230f5f"

        self.db_config = {
            "qa_db": {
                "id": self.faq_db_id,
                "display_name": "FAQ Database"
            },
            "anc_db": {
                "id": self.anc_db_id,
                "display_name": "Announcements Database"
            }
        }
    
    # retrieve all rows from a notion db as list of dictionaries and filter by specified arguments if provided

    # currently only filters for one column and value, will update later to allow for multiple filters using dictionary
    def get_db_rows(self, db_name: str, filter_column: str = None, filter_value: str = None, return_format: str = "unified"):
        
        db_config = self.db_config.get(db_name.lower())
        if not db_config:
            return []

        database_id = db_config["id"]

        try:

            query_params = {"database_id": database_id}
            
            if filter_column and filter_value:
                query_params["filter"] = {
                    "property": filter_column,
                    "text": {
                        "equals": filter_value
                    }
                }
            
            res = self.notion.databases.query(**query_params)
            rows = res.get("results", [])
            extracted_data = []

            if rows:
                for row in rows:
                    props = row.get("properties", {})
                    row_data = {}
                    
                    row_data['id'] = row.get('id')
                    
                    for col_name, col_val in props.items():
                        row_data[col_name] = extract_property_value(col_val)
                    
                    extracted_data.append(row_data)

        # returns empty list - will prevent bot from crashing if 
        # polling a db that doesn't exist
        except Exception as e:
            extracted_data = []

        """
        Example return with announcement database
        {
            {
            'id': 'page-123',
            'Announcement': {'value': 'Hello world!', 'type': 'text', 'formatted': 'Hello world!'},
            'Time': {'value': '2025-09-23T21:00:00', 'type': 'date', 'formatted': '2025-09-23T21:00:00'},
            'Announcement Sent': {'value': 'Not Sent', 'type': 'status', 'formatted': 'Not Sent'}
            },
            {
            'id': 'page-456',
            'Announcement': {'value': 'Init rocks!', 'type': 'text', 'formatted': 'Init rocks!'},
            'Time': {'value': '2025-09-23T21:00:00', 'type': 'date', 'formatted': '2025-09-23T21:00:00'},
            'Announcement Sent': {'value': 'Done', 'type': 'status', 'formatted': 'Done'}
            }
        } 
        """
        return extracted_data
    
    # get announcements that are scheduled to be 
    # sent within 7 minutes (ellie's choice) and have status "Not Sent"
    def get_pending_announcements(self):

        try:

            all_announcements = self.get_db_rows("anc_db", return_format = "unified")
            if not all_announcements:
                return []
            
            # current time in EDT
            edt = pytz.timezone('US/Eastern')
            now = datetime.now(edt)
            cutoff_time = now + timedelta(minutes = 7)
            
            pending = []
            
            for announcement in all_announcements:
                
                if announcement.get("Announcement Sent", {}).get("value") != "Not Sent":
                    continue
                
                # get announcement time
                time_str = announcement.get("Time", {}).get("value")
                if not time_str:
                    continue
                
                try:
                    # parse time -> convert to EDT
                    announcement_time = self._parse_notion_datetime(time_str)
                    if announcement_time.tzinfo is None:
                        announcement_time = edt.localize(announcement_time)
                    
                    # check is annc is within 7 min OR past due
                    if announcement_time <= cutoff_time:
                        # Strip ``` markers from announcement text
                        announcement_text = announcement.get("Announcement", {}).get("formatted", "")
                        if announcement_text.startswith("```") and announcement_text.endswith("```"):
                            # Remove ``` from beginning and end
                            cleaned_text = announcement_text[3:-3].strip()
                        else:
                            cleaned_text = announcement_text
                        
                        # process hyperlinks: convert [text]&(link) to [text](link)
                        cleaned_text = self.process_hyperlinks(cleaned_text)
                        
                        # update announcement with cleaned text
                        announcement["Announcement"]["formatted"] = cleaned_text
                        announcement["Announcement"]["value"] = cleaned_text
                        
                        pending.append(announcement)
                        
                except Exception as e:
                    continue
            
            return pending
            
        except Exception as e:
            return []
    
    # parse Notion datetime string into Python datetime object
    def _parse_notion_datetime(self, datetime_str: str):

        # handles timezone-aware strings (ex: 2025-09-23T21:00:00.000-04:00)
        if re.search(r'[+-]\d{2}:\d{2}$', datetime_str):
            tz_match = re.search(r'([+-]\d{2}):(\d{2})$', datetime_str)
            if tz_match:
                tz_hours = int(tz_match.group(1))
                tz_minutes = int(tz_match.group(2))
                
                # remove timezone and parse
                clean_str = re.sub(r'[+-]\d{2}:\d{2}$', '', datetime_str)
                
                for fmt in ["%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"]:
                    try:
                        naive_dt = datetime.strptime(clean_str, fmt)
                        return naive_dt.replace(tzinfo=pytz.FixedOffset(tz_hours * 60 + tz_minutes))
                    except ValueError:
                        continue
        
        clean_str = re.sub(r'[+-]\d{2}:\d{2}$', '', datetime_str)
        formats = ["%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]
        
        for fmt in formats:
            try:
                return datetime.strptime(clean_str, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse datetime: {datetime_str}")
    
    # process hyperlinks in announcement text by 
    # converting [text]&(link) to [text](link)
    def process_hyperlinks(self, text):

        import re
        
        pattern = r'\[([^\]]+)\]&\(([^)]+)\)'
        
        processed_text = re.sub(pattern, r'[\1](\2)', text)
        
        return processed_text
    
    # marks an announcement as sent by updating its status to 'Done'
    def mark_announcement_sent(self, announcement_row: dict):
        
        try:

            page_id = announcement_row.get('id')
            
            if not page_id:
                return False
            
            update_data = {
                "properties": {
                    "Announcement Sent": {
                        "status": {
                            "name": "Done"
                        }
                    }
                }
            }
            
            self.notion.pages.update(page_id=page_id, **update_data)
            
            return True
            
        except Exception as e:
            return False 