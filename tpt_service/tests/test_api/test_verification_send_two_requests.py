from tpt_service.tests.utils import get_sample, send_signed_request


def test_verification_send_two_requests(client):
    data = {
        "activity": {
            "vle_id": "1",
            "activity_type": "assign",
            "activity_id": "1"
        },
        "sample_data": get_sample('1.txt', 'plain/text'),
        "learner_id": "1234",
        "evaluation_id": 12
    }
    response = send_signed_request(client=client, verb='POST', url='/tpt/api/v1/evaluation/new/',
                                   data=data)

    assert response.content_type == 'application/json'
    assert response.status_code == 200

    if 'status_code' not in response.json:
        assert False

    if 'request_id' not in response.json:
        assert False

    assert response.json['status_code'] == '0'

    data = {
        "activity": {
            "vle_id": "1",
            "activity_type": "assign",
            "activity_id": "1"
        },
        "sample_data": get_sample('1.txt', 'plain/text'),
        "learner_id": "12345",
        "evaluation_id": 12
    }

    response = send_signed_request(client=client, verb='POST', url='/tpt/api/v1/evaluation/new/',
                                   data=data)

    data = {
        "activity": {
            "vle_id": "1",
            "activity_type": "assign",
            "activity_id": "1"
        },
        "sample_data": get_sample('1.txt', 'plain/text'),
        "learner_id": "123456",
        "evaluation_id": 12
    }

    response = send_signed_request(client=client, verb='POST', url='/tpt/api/v1/evaluation/new/',
                                   data=data)
    data = {
        "activity": {
            "vle_id": "1",
            "activity_type": "assign",
            "activity_id": "1"
        },
        "sample_data": get_sample('1.txt', 'plain/text'),
        "learner_id": "1234567",
        "evaluation_id": 12
    }
    response = send_signed_request(client=client, verb='POST', url='/tpt/api/v1/evaluation/new/',
                                   data=data)

    data = {
        "activity": {
            "vle_id": "1",
            "activity_type": "assign",
            "activity_id": "1"
        },
        "sample_data": get_sample('2.txt', 'plain/text'),
        "learner_id": "123456789",
        "evaluation_id": 12
    }
    response = send_signed_request(client=client, verb='POST', url='/tpt/api/v1/evaluation/new/',
                                   data=data)
