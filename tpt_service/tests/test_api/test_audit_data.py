from tpt_service.tests.test_api.test_verification import test_verification


def test_audit_data(client):
    test_verification(client)
    evaluation_id = 12

    response = client.get('/api/v1/evaluation/audit/{}/'.format(evaluation_id))

    assert response.content_type == 'application/json'
    assert response.status_code == 200

    if 'audit_data' not in response.json:
        assert False

    if 'include_enrolment' not in response.json['audit_data']:
        assert False

    if 'include_request' not in response.json['audit_data']:
        assert False

    if 'status_code' not in response.json:
        assert False

    assert response.json['status_code'] == '0'


