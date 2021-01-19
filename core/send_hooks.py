from django_cron import CronJobBase, Schedule
from api.models import hook_pre_send

import requests
import json

from core.help_config import CONFIG_PATH

with open(CONFIG_PATH) as f:
    config = json.load(f)
class SendHooks(CronJobBase):
    RUN_EVERY_MINS = 1/10

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'send_hooks_to_general_backend'  

    def do(self):
        start()

def start():

    try:
        hook_save = hook_pre_send.objects.filter(is_send=False)
        for hook in hook_save:
            url = config["general_backend_url_for_webhook_callback"]
            data = hook.data
            res = requests.post(url=url, data=data)
            print(data , res.status_code)
            if res.status_code == 200:
                hook.is_send = True
                hook.save()
    except:
        pass