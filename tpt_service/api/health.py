from flask import jsonify
from tpt_service import app, tpt


@app.route('/api/v1/health/', methods=['GET'])
def system_health():
    app.logger.debug("GET /health/")
    data = tpt.statistics.get_health_data()
    app.logger.debug(data)

    return jsonify(data), 200
