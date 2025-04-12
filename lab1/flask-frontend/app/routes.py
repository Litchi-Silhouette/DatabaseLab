from flask import render_template, request, jsonify
from . import app
from .Backend.Backend import handle_request
import asyncio

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/submit', methods=['POST'])
def submit():
    selected_scenarios = request.json.get('scenarios')
    request_data = request.json.get('data', {})
    
    # Add req_type to the request data
    request_data["req_type"] = selected_scenarios

    # Call the handle_request function asynchronously
    response = asyncio.run(asyncio.to_thread(handle_request, request_data))

    # Return the response to the front-end
    return jsonify(response)