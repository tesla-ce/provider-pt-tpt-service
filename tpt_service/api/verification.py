from flask import request, jsonify
from tpt_service import app, tpt
from .errors import bad_request
from .activity import get_activity_id_for_tpt
from tpt.commons import TPTException
from .decorator import auth_required


@app.route('/tpt/api/v1/evaluation/new/', methods=['POST'])
@auth_required
def new_evaluation():
    app.logger.debug("NEW EVALUATION RECEIVED")

    if not request.json:  # post request does not contain json
        app.logger.debug("ERROR: CAN NOT EVALUATE WITHOUT JSON OBJECT")
        bad_request("JSON request is required")

    sample_data = request.json.get("sample_data")
    learner_id = request.json.get("learner_id")  # get tesla id from json
    evaluation_id = request.json.get("evaluation_id") # get evaluatio id from json
    vle_id = request.json["activity"]["vle_id"]
    activity_type = request.json["activity"]["activity_type"]
    activity_id = request.json["activity"]["activity_id"]

    tpt_act_id = get_activity_id_for_tpt(vle_id=vle_id, activity_id=activity_id,
                                         activity_type=activity_type)

    try:
        req_id = tpt.task.prepare.execute(original_request_id=evaluation_id, user_id=learner_id,
                                          activity_id=tpt_act_id, data=sample_data)
        # code 0 for valid sample
        return jsonify({'status_code': '0', 'request_id': req_id})
    except TPTException as err:
        return bad_request("{}".format(err))


@app.route('/tpt/api/v1/evaluation/audit/<original_request_id>/', methods=['GET'])
@app.route('/tpt/api/v1/evaluation/audit/<original_request_id>/<comparison_id>', methods=['GET'])
def get_audit_data(original_request_id, comparison_id=None):
    app.logger.debug('ENTERING GET /evaluation/audit/<original_request_id>/ endpoint')

    if comparison_id is None:
        audit_data = tpt.request.get_audit_data(original_request_id)
    else:
        audit_data = tpt.request.get_audit_detail_data(original_request_id, comparison_id)

    audit_data = {
        "include_enrolment": 0,
        "include_request": 0,
        "audit_data": audit_data
    }

    app.logger.debug('EXITING GET /evaluation/audit/<original_request_id>/ endpoint')
    return jsonify({'status_code': '0', 'audit_data': audit_data})
