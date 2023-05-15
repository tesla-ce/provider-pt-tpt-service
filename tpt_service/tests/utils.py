import base64
import os
import requests
from time import time
import json
import hmac
import hashlib

def get_sample(path, mime_type):
    # format: filename:<file>,data:<mime_type>;base64,<data64>
    file_out = os.path.abspath('./tpt_service/tests/documents/{}'.format(path))
    # with codecs.open(file_out, mode="rb", encoding='utf-8', errors='ignore') as file:
    with open(file_out, 'rb') as file:
        file_content = file.read()
        data_b64 = base64.b64encode(file_content)
        filename = path.split(os.path.sep)[-1]

        return "filename:{},data:{};base64,{}".format(filename, mime_type,
                                                      data_b64.decode('utf8'))

def send_signed_request(client, verb, url, data):

    secret = os.getenv('TPT_SECRET', None)
    api_url = os.getenv('API_URL', None)

    if secret is None:
        raise Exception('TPT_SECRET is None')

    if api_url is None:
        raise Exception('API_URL is None')

    #data['nonce'] = int(time() * 1000)

    headers = {
        "Content-Type": "application/json",
    }

    request = requests.Request(verb, '{}{}'.format(api_url, url), data=json.dumps(data),
                               headers=headers)
    prepped = request.prepare()
    signature = hmac.new(secret.encode('utf8'), prepped.body.encode('utf8'), digestmod=hashlib.sha512)
    headers['Content-Length'] = prepped.headers.get('Content-Length')
    headers['TPT-SIGN'] = signature.hexdigest()

    if verb == 'POST':
        response = client.post(url, data=json.dumps(data), headers=headers)

    # response = s.send(prepped, verify=False)

    return response
