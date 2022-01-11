import base64
import json
import requests
# from deepface import DeepFace

# df = DeepFace.find(img_path="sample1.jpg", db_path="./faces", enforce_detection=True)
# df = DeepFace.find(img_path="sample1.jpg", db_path="./faces", enforce_detection=True)

encodedImage = base64.b64encode(open("sample1.jpg", "rb").read())

# Setup separate json data
# payload = {"img": [encodedImage], "db_path": "./faces"}
# POST!
url = "http://52.90.60.140:5000/upload"
payload = {"img": encodedImage}
headers = {'content-type': 'application/json'}

response = requests.post(url, files=payload, headers=headers)

print(response.text)
