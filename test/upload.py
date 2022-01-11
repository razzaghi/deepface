import base64
import json

import requests

# from deepface import DeepFace

# df = DeepFace.find(img_path="sample1.jpg", db_path="./faces", enforce_detection=True)
# df = DeepFace.find(img_path="sample1.jpg", db_path="./faces", enforce_detection=True)

encodedImage = "data:image/jpeg;base64,"+base64.b64encode(open("sample1.jpg", "rb").read()).decode("UTF-8")

# Setup separate json data
# POST!
# url = "http://52.90.60.140:5000/upload"
upload_url = "http://192.168.1.104:5000/upload"
find_url = "http://192.168.1.104:5000/find"
headers = {'content-type': 'application/json'}

# Setup separate json data
upload_payload = {"image_name": "sample1.jpg", "img": encodedImage}
find_payload = {"img": encodedImage}

response = requests.post(url, json=payload,)

# print(response.text)
