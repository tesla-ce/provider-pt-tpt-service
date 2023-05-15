from flask import make_response, jsonify
from tpt_service import app


@app.errorhandler(400)
def bad_request(msg):
    return make_response(jsonify({'error': 'Bad request', 'message': str(msg)}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found', 'message': str(error)}), 404)
