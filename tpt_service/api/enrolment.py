from tpt_service import app
from .errors import not_found


@app.route('/tpt/api/v1/enrolment/sample/', methods=['POST'])
def sample_enrol():
    """
    Our instrument does not require enrolment
    """
    app.logger.debug('POST /enrolment/sample endpoint')
    return not_found(error="Enrolment process not found")
