import json
from flask import render_template
from tpt_service import tpt, app


@app.route('/report/comparisons/<original_request_id>/', methods=['GET'])
def detail_report(original_request_id):
    audit_data = tpt.request.get_audit_data(original_request_id=original_request_id)

    return render_template('report_comparisons.html', original_request_id=original_request_id,
                           audit_data=audit_data)


@app.route('/report/detail/<original_request_id>/<b_request_id>/', methods=['GET'])
def detail_comparison(original_request_id, b_request_id):
    audit_detail_data = tpt.request.get_audit_detail_data(original_request_id=original_request_id,
                                                          b_request_id=b_request_id)

    return render_template('report_comparison.html', original_request_id=original_request_id,
                           audit_detail_data=audit_detail_data, audit_detail_data_json=json.dumps(audit_detail_data))
