import re

def clean_phone_number(phone):
    
    cleaned = re.sub(r'\D', '', phone)
    if len(cleaned) == 10 and cleaned.startswith('09'):
        return cleaned
    elif len(cleaned) == 9 and cleaned.startswith('9'):
        cleaned = '0' + cleaned
        return cleaned
    elif len(cleaned) == 12 and cleaned.startswith('251'):
        cleaned = cleaned[3:]
        return cleaned
    elif len(cleaned) == 8:
        cleaned = '09' + cleaned
        return cleaned
    elif len(cleaned) > 10:
        cleaned = cleaned[:10]
        return cleaned
    elif len(cleaned) > 0:
        return cleaned
    else:
        # print(f"Returning None for invalid number: {phone}") #added for debugging
        return None
