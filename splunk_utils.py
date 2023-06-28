import requests
import xmltodict
import sys

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

def splunk_create_hec(ip, name, index):
    print(f"Creating Splunk HEC called '{name}' for instance {ip}")

    url = f"https://{ip}:8089/services/data/inputs/http"
    data = {
        'name': name,
        'index' : index
    }
    res = requests.post(url=url, data=data, auth=("admin", "5up3rn0va"), verify=False)
    data = xmltodict.parse(res.content)
    print("\n")
    return get_token_from_response(data)
    
def splunk_delete_hec(ip, name):
    print(f"Deleting Splunk HEC called '{name}' for instance {ip}")
    url = f"https://{ip}:8089/services/data/inputs/http/{name}"
    res = requests.delete(url=url, auth=("admin", "5up3rn0va"), verify=False)
    print("\n")
