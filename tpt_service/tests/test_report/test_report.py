
def test_report_detail(client):
    evaluation_id = 1
    response = client.get('/report/comparisons/{}/'.format(evaluation_id))

    assert response.content_type == 'text/html; charset=utf-8'
    assert response.status_code == 200

    assert response.data.decode("utf-8").find('TODO')


def test_report_detail_comparison(client):
    evaluation_id = 1
    comparison_id = 1
    response = client.get('/report/detail/{}/{}/'.format(evaluation_id, comparison_id))

    assert response.content_type == 'text/html; charset=utf-8'
    assert response.status_code == 200

    assert response.data.decode("utf-8").find('TODO')


