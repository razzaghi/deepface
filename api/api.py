import base64
import re
import warnings
from io import BytesIO

from flask_cors import CORS, cross_origin

from db.db import db_init, db_select, db_insert
from utils.utils import get_image_slug

warnings.filterwarnings("ignore")

import os
import PIL.Image as Image

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# ------------------------------

from flask import Flask, jsonify, request, send_file

import argparse
import uuid
import time

# ------------------------------

import tensorflow as tf

tf_version = int(tf.__version__.split(".")[0])
os.environ["CUDA_VISIBLE_DEVICES"]=""
# ------------------------------

if tf_version == 2:
    import logging

    tf.get_logger().setLevel(logging.ERROR)

# ------------------------------

from deepface import DeepFace

# ------------------------------

app = Flask(__name__)
CORS_ALLOW_ORIGIN = "*,*"
CORS_EXPOSE_HEADERS = "*,*"
CORS_ALLOW_HEADERS = "*,*"
cors = CORS(app, resources={r"/api/*": {"origins": "*"}}, origins=CORS_ALLOW_ORIGIN.split(","),
            allow_headers=CORS_ALLOW_HEADERS.split(","), expose_headers=CORS_EXPOSE_HEADERS.split(","),
            supports_credentials=True)
# cors = CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
# app.config['CORS_HEADERS'] = 'Content-Type'

# ------------------------------

if tf_version == 1:
    graph = tf.get_default_graph()

db_init()

# ------------------------------
# Service API Interface

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACE_DIR = BASE_DIR + "/faces"


@app.route('/api/')
def index():
    return '<h1>Hello, world!</h1>'


@app.route('/api/analyze', methods=['POST'])
def analyze():
    global graph

    tic = time.time()
    req = request.get_json()
    trx_id = uuid.uuid4()

    # ---------------------------

    if tf_version == 1:
        with graph.as_default():
            resp_obj = analyzeWrapper(req, trx_id)
    elif tf_version == 2:
        resp_obj = analyzeWrapper(req, trx_id)

    # ---------------------------

    toc = time.time()

    resp_obj["trx_id"] = trx_id
    resp_obj["seconds"] = toc - tic

    return resp_obj, 200


def analyzeWrapper(req, trx_id=0):
    resp_obj = jsonify({'success': False})

    instances = []
    if "img" in list(req.keys()):
        raw_content = req["img"]  # list

        for item in raw_content:  # item is in type of dict
            instances.append(item)

    if len(instances) == 0:
        return jsonify({'success': False, 'error': 'you must pass at least one img object in your request'}), 205

    print("Analyzing ", len(instances), " instances")

    # ---------------------------

    detector_backend = 'opencv'

    actions = ['emotion', 'age', 'gender', 'race']

    if "actions" in list(req.keys()):
        actions = req["actions"]

    if "detector_backend" in list(req.keys()):
        detector_backend = req["detector_backend"]

    # ---------------------------

    try:
        resp_obj = DeepFace.analyze(instances, actions=actions)
    except Exception as err:
        print("Exception: ", str(err))
        return jsonify({'success': False, 'error': str(err)}), 205

    # ---------------
    # print(resp_obj)
    return resp_obj


def analyze_func(img):
    detector_backend = 'opencv'
    actions = ('emotion', 'age', 'gender', 'race',)

    result = {}
    try:
        result = DeepFace.analyze(img_path=img, actions=actions, detector_backend=detector_backend)
    except Exception as err:
        print("Exception: ", str(err))
        result = {}

    # ---------------
    # print(resp_obj)
    return result


@app.route('/api/verify', methods=['POST'])
def verify():
    global graph

    tic = time.time()
    req = request.get_json()
    trx_id = uuid.uuid4()

    resp_obj = jsonify({'success': False})

    if tf_version == 1:
        with graph.as_default():
            resp_obj = verifyWrapper(req, trx_id)
    elif tf_version == 2:
        resp_obj = verifyWrapper(req, trx_id)

    # --------------------------

    toc = time.time()

    resp_obj["trx_id"] = trx_id
    resp_obj["seconds"] = toc - tic

    return resp_obj, 200


def verifyWrapper(req, trx_id=0):
    resp_obj = jsonify({'success': False})

    model_name = "VGG-Face";
    distance_metric = "cosine";
    detector_backend = "opencv"
    if "model_name" in list(req.keys()):
        model_name = req["model_name"]
    if "distance_metric" in list(req.keys()):
        distance_metric = req["distance_metric"]
    if "detector_backend" in list(req.keys()):
        detector_backend = req["detector_backend"]

    # ----------------------

    instances = []
    if "img" in list(req.keys()):
        raw_content = req["img"]  # list

        for item in raw_content:  # item is in type of dict
            instance = []
            img1 = item["img1"];
            img2 = item["img2"]

            validate_img1 = False
            if len(img1) > 11 and img1[0:11] == "data:image/":
                validate_img1 = True

            validate_img2 = False
            if len(img2) > 11 and img2[0:11] == "data:image/":
                validate_img2 = True

            if validate_img1 != True or validate_img2 != True:
                return jsonify(
                    {'success': False, 'error': 'you must pass both img1 and img2 as base64 encoded string'}), 205

            instance.append(img1);
            instance.append(img2)
            instances.append(instance)

    # --------------------------

    if len(instances) == 0:
        return jsonify({'success': False, 'error': 'you must pass at least one img object in your request'}), 205

    print("Input request of ", trx_id, " has ", len(instances), " pairs to verify")

    # --------------------------

    try:
        resp_obj = DeepFace.verify(instances
                                   , model_name=model_name
                                   , distance_metric=distance_metric
                                   , detector_backend=detector_backend
                                   )

        if model_name == "Ensemble":  # issue 198.
            for key in resp_obj:  # issue 198.
                resp_obj[key]['verified'] = bool(resp_obj[key]['verified'])

    except Exception as err:
        resp_obj = jsonify({'success': False, 'error': str(err)}), 205

    return resp_obj


@app.route('/api/represent', methods=['POST'])
def represent():
    global graph

    tic = time.time()
    req = request.get_json()
    trx_id = uuid.uuid4()

    resp_obj = jsonify({'success': False})

    if tf_version == 1:
        with graph.as_default():
            resp_obj = representWrapper(req, trx_id)
    elif tf_version == 2:
        resp_obj = representWrapper(req, trx_id)

    # --------------------------

    toc = time.time()

    resp_obj["trx_id"] = trx_id
    resp_obj["seconds"] = toc - tic

    return resp_obj, 200


def representWrapper(req, trx_id=0):
    resp_obj = jsonify({'success': False})

    # -------------------------------------
    # find out model

    model_name = "VGG-Face"
    distance_metric = "cosine"
    detector_backend = 'opencv'

    if "model_name" in list(req.keys()):
        model_name = req["model_name"]

    if "detector_backend" in list(req.keys()):
        detector_backend = req["detector_backend"]

    # -------------------------------------
    # retrieve images from request

    img = ""
    if "img" in list(req.keys()):
        img = req["img"]  # list
    # print("img: ", img)

    validate_img = False
    if len(img) > 11 and img[0:11] == "data:image/":
        validate_img = True

    if validate_img != True:
        print("invalid image passed!")
        return jsonify({'success': False, 'error': 'you must pass img as base64 encoded string'}), 205

    # -------------------------------------
    # call represent function from the interface

    try:

        embedding = DeepFace.represent(img
                                       , model_name=model_name
                                       , detector_backend=detector_backend
                                       )

    except Exception as err:
        print("Exception: ", str(err))
        resp_obj = jsonify({'success': False, 'error': str(err)}), 205

    # -------------------------------------

    # print("embedding is ", len(embedding)," dimensional vector")
    resp_obj = {}
    resp_obj["embedding"] = embedding

    # -------------------------------------

    return resp_obj


@app.route('/api/image/', methods=['GET'])
@cross_origin()
def image():
    args = request.args
    return send_file(FACE_DIR + "/" + args.get("name"), mimetype='image/gif')


@app.route('/api/upload', methods=['POST'])
@cross_origin()
def upload():
    global graph

    tic = time.time()
    req = request.get_json(force=True)

    # req = json. request.get_json()
    trx_id = uuid.uuid4()

    resp_obj = uploadWrapper(req, trx_id)

    toc = time.time()

    # resp_obj["trx_id"] = trx_id
    # resp_obj["seconds"] = toc - tic

    return resp_obj, 200


def uploadWrapper(req, trx_id=0):
    resp_obj = jsonify({'success': False})

    slug = str(uuid.uuid1())
    image_name = slug + ".jpg"
    person_name = ""
    if "person_name" in list(req.keys()):
        person_name = req["person_name"]

    # -------------------------------------
    # retrieve images from request

    img = ""
    if "img" in list(req.keys()):
        img = req["img"]  # list

    # print("img: ", img)
    # print("img: ", req["img"][0])

    validate_img = False
    if len(img) > 11 and img[0:11] == "data:image/":
        validate_img = True

    if validate_img != True:
        return jsonify({'success': False, 'error': 'you must pass img as base64 encoded string'}), 205

    # -------------------------------------
    # call represent function from the interface

    if not os.path.exists(FACE_DIR):
        os.mkdir(FACE_DIR)

    try:
        image_data = re.sub('^data:image/.+;base64,', '', img)
        img_file = Image.open(BytesIO(base64.b64decode(image_data)))
        img_file = img_file.convert('RGB')
        img_file.save(f'{FACE_DIR}/{image_name}', "JPEG")
        record = db_insert(slug=slug, name=person_name)
        if record:
            os.remove(FACE_DIR + "/representations_facenet.pkl")

    except Exception as err:
        print("Exception: ", str(err))
        resp_obj = jsonify({'success': False, 'error': str(err)}), 205

    # -------------------------------------

    # print("embedding is ", len(embedding)," dimensional vector")
    resp_obj = {'success': True, 'message': "OK"}

    # -------------------------------------

    return resp_obj


def isFaceWrapper(req):
    model_name = "VGG-Face"
    distance_metric = "cosine"
    detector_backend = 'opencv'

    if "model_name" in list(req.keys()):
        model_name = req["model_name"]

    if "detector_backend" in list(req.keys()):
        detector_backend = req["detector_backend"]

    # -------------------------------------
    # retrieve images from request

    img = ""
    if "img" in list(req.keys()):
        img = req["img"]  # list

    # print("img: ", img)

    validate_img = False
    if len(img) > 11 and img[0:11] == "data:image/":
        validate_img = True

    if validate_img != True:
        print("invalid image passed!")
        return None

    result = None
    try:
        face = DeepFace.detectFace(img_path=img, target_size=(400, 400,), detector_backend="opencv")
        result = True
    except Exception as err:
        result = None
        print(err)

    return result


@app.route('/api/isFace', methods=['POST'])
@cross_origin()
def isFace():
    global graph

    req = request.get_json()

    wrapper_response = None
    resp_obj = {}
    resp_obj['isFace'] = False
    if tf_version == 1:
        with graph.as_default():
            wrapper_response = isFaceWrapper(req)
    elif tf_version == 2:
        wrapper_response = isFaceWrapper(req)

    if wrapper_response:
        resp_obj['isFace'] = True

    return resp_obj, 200


@app.route('/api/find', methods=['POST'])
@cross_origin()
def find():
    global graph

    tic = time.time()
    req = request.get_json()
    trx_id = uuid.uuid4()

    wrapper_response = None
    resp_obj = {}
    if tf_version == 1:
        with graph.as_default():
            wrapper_response = findWrapper(req)
    elif tf_version == 2:
        wrapper_response = findWrapper(req)

    if wrapper_response:
        if wrapper_response == -1:
            resp_obj['name'] = "-1"
            return resp_obj, 200
        slug = get_image_slug(wrapper_response)
        analyze_result = analyze_func(req['img'])

        print("-------------------------")
        print(analyze_result)
        print(analyze_result["dominant_emotion"])
        print(analyze_result["age"])
        print(analyze_result["gender"])
        print(analyze_result["dominant_race"])
        person_name = db_select(slug=slug)
        print(person_name)
        print("-------------------------")
        resp_obj['name'] = person_name
        resp_obj['slug'] = slug
        if analyze_result:
            resp_obj['emotion'] = analyze_result["dominant_emotion"]
            resp_obj['age'] = analyze_result["age"]
            resp_obj['gender'] = analyze_result["gender"]
            resp_obj['race'] = analyze_result["dominant_race"]

    return resp_obj, 200


def findWrapper(req):
    # -------------------------------------
    # find out model

    model_name = "VGG-Face"
    distance_metric = "cosine"
    detector_backend = 'opencv'

    if "model_name" in list(req.keys()):
        model_name = req["model_name"]

    if "detector_backend" in list(req.keys()):
        detector_backend = req["detector_backend"]

    # -------------------------------------
    # retrieve images from request

    img = ""
    if "img" in list(req.keys()):
        img = req["img"]  # list

    # print("img: ", img)

    if isFaceWrapper(req):
        img = req["img"]
        result = None
        try:
            embedding = DeepFace.find(
                img_path=img
                , db_path=FACE_DIR
                , model_name="Facenet"
                , detector_backend=detector_backend
            )
            print("========================")
            print(len(embedding["identity"]))
            print(embedding["identity"])
            print("========================")
            if len(embedding["identity"]) > 0:

                result = embedding["identity"][0]
            else:
                result = None
                # resp_obj["success"] = False
                # resp_obj["file_slug"] = None
        except Exception as err:
            print("=================")
            print(err)
            print("=================")
            result = None

        return result
    else:
        return -1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p', '--port',
        type=int,
        default=5000,
        help='Port of serving api')
    args = parser.parse_args()
    # app.run(host='0.0.0.0', port=args.port, ssl_context=('/etc/letsencrypt/live/rec.robotsdna.com/fullchain.pem', '/etc/letsencrypt/live/rec.robotsdna.com/privkey.pem'))
    app.run(host='0.0.0.0', port=args.port)
