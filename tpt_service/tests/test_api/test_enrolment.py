
def test_enrolment(client):

    response = client.post('/tpt/api/v1/enrolment/sample/')

    assert response.content_type == 'application/json'
    assert response.status_code == 404
    assert response.json == {'error': 'Not found', 'message': 'Enrolment process not found'}
