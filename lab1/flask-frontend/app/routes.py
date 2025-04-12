from flask import render_template, request, jsonify
from . import app
from .Backend.DataBase import initDB
from .Backend.Requests import handle_request
import asyncio
import json
import os

path='../test.db'
if os.path.exists(path):
    os.remove(path)
initDB(path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/api/submit', methods=['POST'])
def submit():
    selected_scenario = request.json.get('scenario')
    request_data = request.json.get('data', {})
    
    # Add req_type to the request data
    request_data["req_type"] = selected_scenario

    print(f"Received request data: {request_data}")

    # Call the handle_request function asynchronously
    response = asyncio.run(asyncio.to_thread(handle_request, request_data))

    # Return the response to the front-end
    return jsonify(json.dumps(response))