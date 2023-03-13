import re
import os
from flask import Flask, jsonify, request, send_file, redirect, url_for
from flasgger import Swagger, LazyString, LazyJSONEncoder, swag_from
from logging.config import dictConfig

import function

UPLOAD_FOLDER = '/data'
ALLOWED_EXTENSIONS = {'csv'}

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            }
        },
        "root": {"level": "DEBUG", "handlers": ["console"]},
    }
)

app = Flask(__name__)
app.json_encoder = LazyJSONEncoder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
swagger_template = dict(
    info = {
        'title': LazyString(lambda: 'API Documentation'),
        'version': LazyString(lambda: '1.0.0'),
        'description': LazyString(lambda: 'Documentation for API')
    },
    host = LazyString(lambda: request.host)
)

swagger_config = {
    "headers":[],
    "specs": [
        {
            "endpoint":'docs',
            "route":'/docs.json',
        }
    ],
    "static_url_path":"/flasgger_static",
    "swagger_ui":True,
    "specs_route":"/docs/"
}
swagger = Swagger(app, template=swagger_template, config=swagger_config)

@swag_from("docs/text_processing.yml", methods=['POST'])
@app.route("/text-processing", methods=['POST'])
def text_processing():

    text = request.form.get('text')

    json_response={
        'status_code':200,
        'description': "Scanned Text",
        'data': function.process_text(text)
    }
	
    response_data = jsonify(json_response)
    return response_data

@swag_from("docs/file_processing.yml", methods=['POST'])
@app.route("/file-processing", methods=['POST'])
def file_processing():
    
    upload_file = request.files['filename']
    file_data = upload_file.read()

    # get the name of the uploaded file
    file_name = upload_file.filename
    file_path = os.path.join('data', upload_file.filename)
    file_path = file_path.replace('\\', '/')
    function.process_file(file_path,0)
    
    json_response={
        'status_code':200,
        'file_path': file_path,
        'file_name': file_name
    }
    
	
    response_data= jsonify(json_response)
    # path = "/Examples.pdf"
    # return send_file(path, as_attachment=True)
    return response_data

if __name__ == '__main__':
    app.run()
