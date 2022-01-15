import base64
import json
import uuid

import requests

from robot.db import db_insert, db_select

# select_file = "images/notfound.jpg"
select_file = "images/large3.jpg"
base_address = "http://52.90.60.140:5000"
upload_url = base_address + "/upload"
headers = {'content-typ e': 'application/json'}

def get_image_slug(image):
    parts = str.split(image, "/")
    last_part = parts[len(parts) - 1]
    slug_parts = str.split(last_part, ".")
    return slug_parts[0]


def upload_request(slug):
    base64image = "data:image/jpeg;base64," + base64.b64encode(open(select_file, "rb").read()).decode("UTF-8")
    payload = {"image_name": slug + ".jpg", "img": base64image}
    url = base_address + "/upload"
    response = requests.post(url, json=payload)
    return response


def send_search_request():
    base64image = "data:image/jpeg;base64," + base64.b64encode(open(select_file, "rb").read()).decode("UTF-8")
    payload = {"img": base64image}
    url = base_address + "/find"
    response = requests.post(url, json=payload)
    print(response.text)
    data = json.loads(response.text)
    if data['success']:
        print("Yes")
        slug = get_image_slug(data['file_slug'])
        print(slug)
        person_name = db_select(slug=slug)[0]
        print("Hi " + person_name)
    else:
        name = input("What is your name?")
        slug = str(uuid.uuid1())
        record = db_insert(slug=slug, name=name)
        print("===========================")
        print(record)
        print("===========================")
        response = upload_request(slug=slug)
        print(name)
        print("No")


# db_init()
# db_clear()
send_search_request()
