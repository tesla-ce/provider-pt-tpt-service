import requests
import os
import base64


def get_sample(path, mime_type):
    # format: filename:<file>,data:<mime_type>;base64,<data64>
    file_out = os.path.abspath('./../tests/documents/{}'.format(path))
    # with codecs.open(file_out, mode="rb", encoding='utf-8', errors='ignore') as file:
    with open(file_out, 'rb') as file:
        file_content = file.read()
        data_b64 = base64.b64encode(file_content)
        filename = path.split(os.path.sep)[-1]

        return "filename:{},data:{};base64,{}".format(filename, mime_type,
                                                      data_b64.decode('utf8'))



base_url = 'http://localhost:8081'
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
response = requests.post('{}/api/v1/evaluation/new/'.format(base_url), json=data)
print(response.content)
data = {
    "activity": {
        "vle_id": "1",
        "activity_type": "assign",
        "activity_id": "1"
    },
    "sample_data": get_sample('1.txt', 'plain/text'),
    "learner_id": "6789",
    "evaluation_id": 13
}
response = requests.post('{}/api/v1/evaluation/new/'.format(base_url), json=data)

data = {
    "activity": {
        "vle_id": "1",
        "activity_type": "assign",
        "activity_id": "1"
    },
    "sample_data": get_sample('2.txt', 'plain/text'),
    "learner_id": "101112",
    "evaluation_id": 14
}
response = requests.post('{}/api/v1/evaluation/new/'.format(base_url), json=data)
print(response.content)

assert response.headers['Content-Type'] == 'application/json'
assert response.status_code == 200

if 'status_code' not in response.json():
    assert False

if 'request_id' not in response.json():
    assert False

assert response.json()['status_code'] == '0'