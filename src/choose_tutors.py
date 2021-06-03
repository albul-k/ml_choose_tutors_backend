import os
import dill
import logging
import sys
from flask import Flask, request, make_response, jsonify
from flask_restful import Api
from flask_cors import CORS
from logging.handlers import RotatingFileHandler
from time import strftime
import pandas

sys.path.append('./src/')

# Load pipeline
MODEL = None
with open(os.path.join('src', 'train', 'pipeline.dill'), 'rb') as file:
    MODEL = dill.load(file)

handler = RotatingFileHandler(
    filename='app.log', maxBytes=100000, backupCount=10)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

app = Flask(__name__)
cors = CORS(app, resources={r'*': {'origins': '*'}})
api = Api(app)


@app.route('/check', methods=['GET'])
def check():
    return "It's work!"


@app.route('/predict', methods=['POST'])
def predict():

    if request.is_json:

        X = pandas.DataFrame(
            [list(request.json.values())],
            columns=list(request.json.keys())
        )
        dt = strftime("[%Y-%b-%d %H:%M:%S]")
        logger.info(f'{dt} Data: {str(request.json)}')
        try:
            probability = MODEL.predict_proba(X)[0][1]
            res = make_response(
                jsonify({'probability': round(probability*100, 2), 'success': True}), 200)
            return res
        except Exception as err:
            logger.warning(f'{dt} Exception: {str(err)}')
            res = make_response(
                jsonify({'error': str(err), 'success': False}), 404)
            return res

    res = make_response(
        jsonify({'error': 'The request body is not JSON', 'success': False}), 400)
    return res


if __name__ == '__main__':
    app.run()