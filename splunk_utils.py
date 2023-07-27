import requests
import sys
import json

# url = f"https://{ip}:8089/services/data/inputs/http"
# url = "https://sschimper-marriott.stg.splunkcloud.com/services/data/inputs/http"

def get_token_from_response(data):
    try:
        feed = data.get('feed')
        entry = feed.get('entry')
        content = entry.get('content')
        s_dict = content.get('s:dict')
        props = s_dict.get('s:key')
        for prop in props:
            if(prop['@name'] == 'token'):
                return prop['#text']
        return None
    except Exception as e:
        print(f"Something happened when trying to obtain HEC token from API response: {str(e)}\n Response received is: {data}")
        sys.exit("Aborting!")

def get_headers():
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer eyJraWQiOiJzcGx1bmsuc2VjcmV0IiwiYWxnIjoiSFM1MTIiLCJ2ZXIiOiJ2MiIsInR0eXAiOiJzdGF0aWMifQ.eyJpc3MiOiJhZG1pbiBmcm9tIHNoLWktMDRlMGUyNTYwODVjMGU3OTYiLCJzdWIiOiJhZG1pbiIsImF1ZCI6ImJvdG8zIiwiaWRwIjoiU3BsdW5rIiwianRpIjoiNjA3OGI2ZWNkOGY1YTA4OTBmODE1NDg3Y2Y4Nzg4MmZkZWRhODE0MWI5ZGQ4YTE2ZTA3YTUyYzdmYTUxNGYzZiIsImlhdCI6MTY5MDQ0MzkyMywiZXhwIjoxNjkzMDM1OTIzLCJuYnIiOjE2OTA0NDM5MjN9._o0B_-T3xAjyjGfN8ZU4d6JCkxHiMQrG_0_N-AEXCzRM8DLyGt-UUl-KJ6omClPuIfZPJwtOdr-9WFvwkUEPnQ",
    }

def splunk_create_hec(name, index):
    print(f"Creating Splunk HEC called '{name}'")

    url = "https://staging.admin.splunk.com/scv-shw-b122f8d26c3943/adminconfig/v2/inputs/http-event-collectors"
    headers = get_headers()
    data = {
        "defaultHost": "",
        "defaultIndex": index,
        "defaultSource": "",
        "defaultSourcetype": "",
        "disabled": False,
        "name": name,
    }
    try:
        res = requests.post(url=url, headers=headers, data=json.dumps(data), verify=False)
        res.raise_for_status()
    except Exception as e:
        print(f"Splunk HEC token creation failed: {str(e)}")
        raise e
    print(f"Splunk HEC token creation was successful: {res.text}")
    
def splunk_delete_hec(hec_name):
    print(f"Deleting Splunk HEC called '{hec_name}'.")
    headers = get_headers()
    url = f"https://staging.admin.splunk.com/scv-shw-b122f8d26c3943/adminconfig/v2/inputs/http-event-collectors/{hec_name}"
    res = requests.delete(url=url, headers=headers, verify=False)
    try:
        res = requests.delete(url=url, headers=headers, verify=False)
        # res.raise_for_status() # For some reason I get an 404 error although the HEC token deletion is successful!
    except Exception as e:
        print(f"Splunk HEC token deletion failed: {str(e)}")
        raise e
    print(f"Splunk HEC token deletion was successful: {res.text}")
