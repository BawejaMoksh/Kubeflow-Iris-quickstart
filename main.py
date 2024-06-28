from flask import Flask, json, request, jsonify
import os
import json
import yaml
import urllib.request
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.secret_key = "caircocoders-ednalan"

UPLOAD_FOLDER = '~/Postman/files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


ALLOWED_EXTENSIONS = set(['yaml'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def convert_yaml_to_json(yaml_file_path):
    with open(yaml_file_path, 'r') as yaml_file:

        for data in yaml.load_all(yaml_file):
            yaml_contents = list(yaml.safe_load_all(yaml_file,Loader=yaml.SafeLoader))
    return json.dumps(yaml_contents, indent=4)

@app.route('/')
def main():
    return 'Homepage'


@app.route('/upload', methods=['POST','GET'])
def upload_file():
    # check if the post request has the file part
    if 'files[]' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp

    files = request.files.getlist('files[]')

    errors = {}
    success = False
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            success = True
        else:
            errors[file.filename] = 'File type is not allowed'

    if success and errors:
        errors['message'] = 'File(s) successfully uploaded'
        resp = jsonify(errors)
        resp.status_code = 500
        return resp
    if success:
        resp = jsonify({'message': 'Files successfully uploaded'})

        resp.status_code = 201
        return resp
    else:
        resp = jsonify(errors)
        resp.status_code = 500
        return resp
@app.route('/read_yaml',methods=['GET'])
def read_yaml():
    if 'files[]' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp

    files = request.files.getlist('files[]')
    for file in files:
        if not file or not allowed_file(file.filename):
            resp = jsonify({'message': 'Invalid or missing filename'})
            resp.status_code = 400
            return resp
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        if not os.path.exists(file_path):
            resp = jsonify({'message': 'File not found'})
            resp.status_code = 404
            return resp
        try:
            json_content = convert_yaml_to_json(file_path)
            resp = jsonify(json.loads(json_content))
            # Convert string back to JSON object for response
            # stream = file(file_path, 'r')
            #
            # resp = jsonify({'message' : yaml.load_all(stream)})

            resp.status_code = 200
            return resp
        except Exception as e:
            resp = jsonify({'message': str(e)})
            resp.status_code = 500
            return resp

if __name__ == '__main__':
    app.run(debug=True)