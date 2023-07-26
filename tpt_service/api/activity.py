import base64
from flask import jsonify, request
from tpt_service import tpt, app
from .errors import not_found
import tpt.commons as tpt_commons


def get_activity_id_for_tpt(vle_id, activity_id, activity_type):
    return "{}_{}_{}".format(vle_id, activity_id, activity_type)

"""
@api {post} /api/v1/activity/ Request User information
@apiName Create
@apiGroup Activity

@apiParam {Object} configuration Configuration of activity.
@apiParam {String} configuration[course_id] Course ID of activity.
@apiParam {Datetime} configuration[start_date] Start date of activity.
@apiParam {Datetime} configuration[end_date] Ebd date of activity.
@apiParam {String="auto","c","c++","java","text","text_only","m2","miranda","pascal","assembler"} configuration[type] Type of activity.
@apiParam {String="activity","course","activity_list","all"} configuration[context] Context of activity.
@apiParam {String="activity","course","activity_list","all"} configuration[context] Context of activity.
@apiParam {"Object""} configuration[config] Extra configuration of activity.
"""


@app.route('/tpt/api/v1/activity/', methods=['POST'])
def set_activity():
    app.logger.debug('POST /activity/')
    course_id = request.json["configuration"]["course_id"]
    start_date = request.json["configuration"]["start_date"]
    end_date = request.json["configuration"]["end_date"]

    activity_type = tpt_commons.CmpTypeEnum[request.json["configuration"]["type"]]
    context = tpt_commons.ActContextEnum[request.json["configuration"]["context"]]

    config = request.json["configuration"]["config"]

    statement = None
    if 'statement' in request.json["configuration"]:
        statement = request.json["configuration"]["statement"]

    data_sample = None
    filename = None

    if statement is not None:
        # data = base64.b64decode(data64)
        # format: filename:<file>,data:<mime_type>;base64,<data64>
        parts = statement.split(';')
        data_sample = base64.b64decode(parts[1].split(',')[1])
        filename = parts[0].split(',')[0].split(':')[1]

    tpt_activity_id = get_activity_id_for_tpt(request.json["vle_id"], request.json["activity_id"],
                                              request.json["activity_type"])

    app.logger.debug('tpt_activity_id {}'.format(tpt_activity_id))
    app.logger.debug('start_date {}'.format(start_date))
    app.logger.debug('end_date {}'.format(end_date))
    app.logger.debug('type {}'.format(activity_type))
    app.logger.debug('context {}'.format(context))
    app.logger.debug('config {}'.format(config))
    if data_sample is not None:
        app.logger.debug('data_sample {}'.format(len(data_sample)))
        app.logger.debug('filename {}'.format(filename))
    else:
        app.logger.debug('data_sample is None')

    tpt.activity.prepare(activity_id=tpt_activity_id, course_id=course_id, start_date=start_date,
                         end_date=end_date, activity_type=activity_type, context=context,
                         config=config, data=data_sample, path=filename)

    return jsonify({'status_code': '0'})


@app.route('/tpt/api/v1/activity/<vle_id>/<activity_id>/<activity_type>/', methods=['GET'])
def get_activity(vle_id, activity_id, activity_type):
    app.logger.debug('GET /activity/{}/{}/{}'.format(vle_id, activity_id, activity_type))
    tpt_activity_id = get_activity_id_for_tpt(vle_id, activity_id, activity_type)

    # read from database
    activity = tpt.activity.get_config(tpt_activity_id)

    if activity is None:
        return not_found("Activity not found")
    activity_configuration = {"course_id": activity.course_id, "start_date": activity.start_date,
                              "end_date": activity.end_date, "type": activity.activity_type.name,
                              "context": activity.context.name, "config": activity.config}
    app.logger.debug(activity_configuration)
    return jsonify({'status_code': '0', 'activity_configuration': activity_configuration})


@app.route('/tpt/api/v1/activity/<vle_id>/<activity_id>/<activity_type>/', methods=['DELETE'])
def delete_activity(vle_id, activity_id, activity_type):
    app.logger.debug('DELETE /activity/{}/{}/{}'.format(vle_id, activity_id, activity_type))
    tpt_activity_id = get_activity_id_for_tpt(vle_id, activity_id, activity_type)
    tpt.activity.delete(activity_id=tpt_activity_id)

    return jsonify({'status_code': '0'})


@app.route('/tpt/api/v1/activity/archive/<vle_id>/<activity_id>/<activity_type>/', methods=['POST'])
def archive_activity(vle_id, activity_id, activity_type):
    app.logger.debug('POST /activity/archive/{}/{}/{}'.format(vle_id, activity_id, activity_type))
    tpt_activity_id = get_activity_id_for_tpt(vle_id, activity_id, activity_type)
    tpt.activity.archive_data(activity_id=tpt_activity_id)

    return jsonify({'status_code': '0'})
