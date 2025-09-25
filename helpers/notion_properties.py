# extract value from any Notion property type and return a unified format
# returns a dictionary with 'value', 'type', and 'formatted' keys

def extract_property_value(val):
    
    prop_type = val.get("type", "unknown")
    
    if prop_type == "title":
        title_list = val.get("title", [])

        text_value = "".join([item.get("plain_text", "") for item in title_list])
        return {
            "value": text_value,
            "type": "text",
            "formatted": text_value
        }
    
    elif prop_type == "rich_text":
        rt_list = val.get("rich_text", [])

        text_value = "".join([item.get("plain_text", "") for item in rt_list])
        return {
            "value": text_value,
            "type": "text", 
            "formatted": text_value
        }
    
    elif prop_type == "text":
        text_value = val.get("text", {}).get("content", "")
        return {
            "value": text_value,
            "type": "text",
            "formatted": text_value
        }
    
    elif prop_type == "date":
        date_obj = val.get("date")
        if date_obj:
            start_date = date_obj.get("start", "")
            end_date = date_obj.get("end", "")
            formatted_date = start_date
            if end_date and end_date != start_date:
                formatted_date = f"{start_date} to {end_date}"
            return {
                "value": start_date,
                "type": "date",
                "formatted": formatted_date,
                "raw": date_obj
            }
        return {
            "value": None,
            "type": "date",
            "formatted": "No date set"
        }
    
    elif prop_type == "select":
        select_obj = val.get("select")
        if select_obj:
            return {
                "value": select_obj.get("name", ""),
                "type": "select",
                "formatted": select_obj.get("name", ""),
                "color": select_obj.get("color", "")
            }
        return {
            "value": None,
            "type": "select", 
            "formatted": "No selection"
        }
    
    elif prop_type == "status":
        status_obj = val.get("status")
        if status_obj:
            return {
                "value": status_obj.get("name", ""),
                "type": "status",
                "formatted": status_obj.get("name", ""),
                "color": status_obj.get("color", "")
            }
        return {
            "value": None,
            "type": "status",
            "formatted": "No status"
        }
    
    elif prop_type == "multi_select":
        multi_select_list = val.get("multi_select", [])
        values = [item.get("name", "") for item in multi_select_list]
        formatted = ", ".join(values) if values else "No selections"
        return {
            "value": values,
            "type": "multi_select",
            "formatted": formatted
        }
    
    elif prop_type == "number":
        number_value = val.get("number")
        return {
            "value": number_value,
            "type": "number",
            "formatted": str(number_value) if number_value is not None else "No number"
        }
    
    elif prop_type == "checkbox":
        checkbox_value = val.get("checkbox", False)
        return {
            "value": checkbox_value,
            "type": "checkbox",
            "formatted": "✅" if checkbox_value else "❌"
        }
    
    elif prop_type == "url":
        url_value = val.get("url", "")
        return {
            "value": url_value,
            "type": "url",
            "formatted": url_value
        }
    
    elif prop_type == "email":
        email_value = val.get("email", "")
        return {
            "value": email_value,
            "type": "email",
            "formatted": email_value
        }
    
    elif prop_type == "phone_number":
        phone_value = val.get("phone_number", "")
        return {
            "value": phone_value,
            "type": "phone",
            "formatted": phone_value
        }
    
    else:

        return {
            "value": str(val),
            "type": "unknown",
            "formatted": str(val)
        }
