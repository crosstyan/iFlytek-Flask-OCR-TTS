import json

def json_parser(json_file):
    data=json.load(json_file)
    result=''
    for each in data['data']['document']['blocks']:
        result+=(each['lines'][0]['text'])+"\n"
    return result

with open(r"data.json", encoding="UTF-8")  as json_file:
    text=json_parser(json_file)
    print (text)