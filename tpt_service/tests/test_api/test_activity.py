data = {
    'configuration': {
        'course_id': '1',
        'context': 'ACTIVITY',
        'start_date': '2021-01-01 00:00:00',
        'end_date': '2022-01-01 00:00:00',
        'type': 'AUTO',
        'config': '{}',
        'statement': None,

    },
    'vle_id': '1',
    'activity_id': '1',
    'activity_type': 'assign'
}


def test_activity_create(client):
    response = client.post('/tpt/api/v1/activity/', json=data)

    assert response.content_type == 'application/json'
    assert response.status_code == 200
    assert response.json == {'status_code': '0'}


def test_activity_get(client):
    response = client.get('/tpt/api/v1/activity/{}/{}/{}/'.format(
        data['vle_id'], data['activity_id'], data['activity_type']
    ))

    assert response.content_type == 'application/json'
    assert response.status_code == 200

    assert response.json['status_code'] == '0'
    assert response.json['activity_configuration']['config'] == data['configuration']['config']
    assert response.json['activity_configuration']['context'] == data['configuration']['context']
    assert response.json['activity_configuration']['course_id'] == data['configuration']['course_id']
    assert response.json['activity_configuration']['type'] == data['configuration']['type']


def test_activity_archive(client):
    response = client.post('/tpt/api/v1/activity/archive/{}/{}/{}/'.format(
        data['vle_id'], data['activity_id'], data['activity_type']
    ))

    assert response.content_type == 'application/json'
    assert response.status_code == 200

    assert response.json['status_code'] == '0'


def test_activity_delete(client):
    response = client.delete('/tpt/api/v1/activity/{}/{}/{}/'.format(
        data['vle_id'], data['activity_id'], data['activity_type']
    ))

    assert response.content_type == 'application/json'
    assert response.status_code == 200

    assert response.json['status_code'] == '0'
