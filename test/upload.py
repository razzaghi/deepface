import base64

import requests

# from deepface import DeepFace

# df = DeepFace.find(img_path="sample1.jpg", db_path="./faces", enforce_detection=True)
# df = DeepFace.find(img_path="sample1.jpg", db_path="./faces", enforce_detection=True)

upload_file_name = "not-related.jpg"
search_file_name = "notfound.jpg"

uploadImage = "data:image/jpeg;base64," + base64.b64encode(open(upload_file_name, "rb").read()).decode("UTF-8")
findImage = "data:image/jpeg;base64," + base64.b64encode(open(search_file_name, "rb").read()).decode("UTF-8")

# Setup separate json data
# POST!
# url = "http://52.90.60.140:5000/upload"
# base_address = "http://192.168.1.104:5000"
base_address = "http://52.90.60.140:5000"
upload_url = base_address + "/upload"
find_url = base_address + "/find"
headers = {'content-typ e': 'application/json'}

# Setup separate json data
upload_payload = {"image_name": upload_file_name, "img": uploadImage}
find_payload = {"img": findImage}

# response = requests.post(upload_url, json=upload_payload, )
response = requests.post(find_url, json=find_payload, )

with open("response.json", "w") as outfile:
    outfile.write(response.text)
