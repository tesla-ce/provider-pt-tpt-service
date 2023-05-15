import requests
import os
import base64
import json
import hmac
import hashlib
import time

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



base_url = 'http://localhost:5000'
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

secret = 'secret_hey'
s = requests.Session()
headers = {"Content-Type": "application/json"}
data['nonce'] = int(time.time() * 1000)

request = requests.Request('POST', '{}/api/v1/evaluation/new/'.format(base_url), data=json.dumps(data),
                           headers=headers)
prepped = request.prepare()
signature = hmac.new(secret.encode('utf8'), prepped.body.encode('utf8'), digestmod=hashlib.sha512)
prepped.headers['TPT-SIGN'] = signature.hexdigest()

response = s.send(prepped)

#response = requests.post('{}/api/v1/evaluation/new/'.format(base_url), json=data)

print(response.content.decode())
