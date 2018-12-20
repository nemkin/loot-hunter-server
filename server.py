#/usr/bin/python3

import os
import json
import pprint

from flask import Flask
from flask import request
from flask import jsonify
from urllib.parse import unquote

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

root = "web"

def dir_shall_exist(dir):
    try:
        os.makedirs(dir)
    except FileExistsError:
        pass

def handle_exception(e):
    message = str(e)
    print(message)
    return jsonify(
        success=False,
        message=message
    )


def remove_empty_folders(dir):
    for item in os.listdir(dir):
        full_path = os.path.join(dir, item)
        if os.path.isdir(full_path):
            remove_empty_folders(full_path)
            if len(os.listdir(full_path)) == 0:
                os.rmdir(full_path)

def directory_structure_to_json(root):   
    result = []
    for item in os.listdir(root):
        if os.path.isdir(os.path.join(root,item)):
            result.append({item: directory_structure_to_json(os.path.join(root, item))})
        if os.path.isfile(os.path.join(root,item)):
            result.append(item)
    return result

@app.route('/<maindir>/<subdir>/<key>', methods = ['GET', 'POST', 'DELETE'])
def saves(maindir, subdir, key):

    try:
        print(pprint.pformat(request.environ, depth=5), "\n", request.get_data())

        global root
        path = os.path.join(root, maindir, subdir)
        dir_shall_exist(path)
        location = os.path.join(path,key)
        
        if request.method == 'GET':
            with open(location, "r") as file:
                load = json.load(file)
            return jsonify(
                success=True,
                result=load
            )

        if request.method == 'POST':
            load = json.loads(unquote(request.get_data(as_text=True)))
            with open(location, "w") as file:
                file.write(json.dumps(load))

        if request.method == 'DELETE':
            os.remove(location)

        return jsonify(
            success=True
        )

    except Exception as e:
        return handle_exception(e)

    finally:
        remove_empty_folders(root)

@app.route('/<maindir>', methods = ['GET'])
def list(maindir):
    
    try:
        global root
        path = os.path.join(root,maindir)
        return jsonify(
            success=True,
            result=directory_structure_to_json(path)
        )

    except Exception as e:
        return handle_exception(e)

if __name__ == "__main__":

    app.run(host='0.0.0.0',port=80)
