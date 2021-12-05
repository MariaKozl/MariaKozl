import requests
from pprint import pprint
import json

username = 'fgfjhdg'

url = f'https://api.github.com/users/{username}/repos'

response = requests.get(url)
j_data = response.json()
pprint(j_data)

with open('j_data.json', 'w') as write_file:
    json.dump(j_data, write_file)


