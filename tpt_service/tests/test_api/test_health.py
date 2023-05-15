
def test_health(client):

    response = client.get('/api/v1/health/')

    assert response.content_type == 'application/json'
    assert response.status_code == 200

    if "requests" not in response.json:
        assert False

    if 'analyzed' not in response.json['requests']:
        assert False

    if 'pending_analyze' not in response.json['requests']:
        assert False

    if 'pending_update' not in response.json['requests']:
        assert False

    if 'prepared' not in response.json['requests']:
        assert False

    if 'processing' not in response.json['requests']:
        assert False
