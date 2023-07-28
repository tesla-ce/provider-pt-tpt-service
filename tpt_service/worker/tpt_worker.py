"""
TPTWorker class
"""
import os
import hashlib
import hmac
import requests
from time import sleep, time
import signal
import json
from tpt.commons import TPTException
from tpt_service.api.utils import get_config_value


class TPTWorker:
    def __init__(self, tasks, logger):
        self.tasks = tasks
        self.kill_thread = False
        self.logger = logger

        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_thread = True

    def run(self, thread_id):
        self.logger.info("TPTWorker thread {} running. Tasks: {}".format(thread_id, self.tasks))

        # Create a TPT object to access the public methods
        from tpt_service import tpt
        tpt.events['onEndAnalysis'] += self.update_request
        while not self.kill_thread:
            try:
                if 'extract' in self.tasks:
                    tpt.task.extract.execute()

                if 'analyse' in self.tasks:
                    tpt.task.analyze.execute()

                if 'compare' in self.tasks:
                    tpt.task.compare.execute()

                if 'update' in self.tasks:
                    tpt.task.update.execute()

            except (TPTException, TypeError) as err:
                self.logger.exception(err)
            except KeyboardInterrupt:
                self.kill_thread = True

            self.logger.debug("TPTWorker thread {} sleeping.".format(thread_id))
            sleep(2)


    def update_request(self, request):
        self.logger.info("TPTWorker update_request {}".format(request))

        if 'request_id' not in request:
            return

        self.logger.info("TPTWorker update_request {}".format(request['request_id']))

        parent_request_id = request['request_id'].split('__')[0]

        data = {
            "request_id": parent_request_id,
            "result": request['result']/100.0,
            "audit_data": request['audit_data']
        }

        secret = get_config_value('API_SECRET')
        api_url = get_config_value('API_URL')

        s = requests.Session()
        data['action'] = 'UPDATE_RESULT'
        data['nonce'] = int(time() * 1000)
        headers = {
            "Content-Type": "application/json",
            "TESLA-TPT-METHOD": "send_result",
            "TESLA-TPT-MESSAGE-ID": str(data['nonce'])
        }

        request = requests.Request('POST', '{}/api/webhooks/'.format(api_url), data=json.dumps(data),
                                   headers=headers)
        prepped = request.prepare()
        signature = hmac.new(secret.encode('utf8'), prepped.body.encode('utf8'), digestmod=hashlib.sha512)
        prepped.headers['TESLA-SIGN'] = signature.hexdigest()
        try:
            response = s.send(prepped, verify=False)

            if int(response.status_code) == 200:
                self.logger.info("TPTWorker update_request FINISHED with SUCCESS")
            else:
                self.logger.error("TPTWorker update_request FINISHED with ERROR")

        except requests.exceptions.RequestException:
            self.logger.error("TPTWorker update_request FINISHED with ERROR")

