from flask import Flask, request, jsonify, send_from_directory
import requests
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/liftwing', methods=['POST'])
def liftwing():
    print("lift")
    data = request.json
    rev_id = data.get('rev_id')
    
    if not rev_id:
        return jsonify({'error': 'No revision ID provided'}), 400

    inference_url = 'https://api.wikimedia.org/service/lw/inference/v1/models/enwiki-damaging:predict'
    headers = {
        'User-Agent': 'WikimediaEventStreamMonitor (https://github.com/ethanedwards/editstream)',
        'Accept': 'application/json'
    }
    payload = {"rev_id": int(rev_id)}

    try:
        app.logger.info(f"Sending request to Liftwing API for rev_id: {rev_id}")
        response = requests.post(inference_url, headers=headers, json=payload)
        response.raise_for_status()
        app.logger.info(f"Received response from Liftwing API: {response.text}")
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error in Liftwing API request: {str(e)}")
        return jsonify({'error': str(e)}), 500
    except json.JSONDecodeError as e:
        app.logger.error(f"Error decoding JSON from Liftwing API: {str(e)}")
        return jsonify({'error': 'Invalid JSON response from Liftwing API'}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error in Liftwing API request: {str(e)}")
        return jsonify({'error': 'Unexpected error occurred'}), 500

if __name__ == '__main__':
    app.run(debug=True)