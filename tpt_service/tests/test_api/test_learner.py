
def test_delete(client):

    learner_id = 1234

    response = client.delete('/tpt/api/v1/learner/{}'.format(learner_id))

    assert response.content_type == 'application/json'
    assert response.status_code == 200
    assert response.json == {"status_code": "0"}
