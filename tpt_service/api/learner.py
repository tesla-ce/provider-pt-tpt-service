from flask import jsonify
from tpt_service import app, tpt


@app.route('/api/v1/learner/<learner_id>', methods=['DELETE'])
def delete_tesla_id(learner_id):
    app.logger.debug("DELETE /learner/{}".format(learner_id))

    tpt.learner.delete_data(user_id=learner_id)

    return jsonify({'status_code': '0'})
