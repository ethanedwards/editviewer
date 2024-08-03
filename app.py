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
    data = request.json
    rev_id = data.get('rev_id')
    
    if not rev_id:
        return jsonify({'error': 'No revision ID provided'}), 400

    inference_url = 'https://api.wikimedia.org/service/lw/inference/v1/models/enwiki-damaging:predict'
    headers = {
        'User-Agent': 'WikimediaEventStreamMonitor (https://github.com/yourusername/yourrepository)',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    payload = {"rev_id": int(rev_id)}

    try:
        app.logger.info(f"Sending request to Liftwing API for rev_id: {rev_id}")
        app.logger.debug(f"Request payload: {payload}")
        response = requests.post(inference_url, headers=headers, json=payload)
        app.logger.debug(f"Response status code: {response.status_code}")
        app.logger.debug(f"Response content: {response.text}")
        
        if response.status_code == 400:
            error_message = response.json().get('detail', 'Unknown error')
            app.logger.warning(f"Bad request to Liftwing API: {error_message}")
            return jsonify({'error': error_message}), 400
        
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error in Liftwing API request: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            app.logger.error(f"Response content: {e.response.text}")
        return jsonify({'error': str(e)}), 500
    except json.JSONDecodeError as e:
        app.logger.error(f"Error decoding JSON from Liftwing API: {str(e)}")
        return jsonify({'error': 'Invalid JSON response from Liftwing API'}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error in Liftwing API request: {str(e)}")
        return jsonify({'error': 'Unexpected error occurred'}), 500

if __name__ == '__main__':
    app.run(debug=True)