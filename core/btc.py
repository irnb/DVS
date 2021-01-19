from django_cron import CronJobBase
from django_cron import Schedule

from api.models import block_save
from api.models import bitcoin_transaction
from api.models import Block_Number

import requests
import json

from core.help_config import CONFIG_PATH
with open(CONFIG_PATH) as f:
    config = json.load(f)


class GetBTCBlock(CronJobBase):
    RUN_EVERY_MINS = 5

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'get_btc_transaction'

    def do(self):
        start()


def start():
    current_blocknum_obj = Block_Number.objects.filter(
        id_for_filter_object=0)[0]
    current_blocknum = current_blocknum_obj.btc

    last_blocknum = requests.get(config["bitcoin_api_lastBlockNumber_url"])
    last_blocknum = int(last_blocknum.text)

    confirm_acceptable_block_num = last_blocknum - 6

    while (confirm_acceptable_block_num > current_blocknum):
        try:
            response = requests.get(
                config["bitcoin_api_getBlockByNumber_url"]+str(current_blocknum))
            print(response)
            for transaction in response.json()['tx']:
                transaction_hash = transaction['hash']
                i = 0
                input_addr = {}
                for x in transaction['inputs']:
                    if 'prev_out' in x:
                        input_addr[i] = x['prev_out']['addr']
                        i += 1
                    else:
                        pass
                transaction_input = json.dumps(input_addr)
                transaction_input = json.loads(transaction_input)
                for output in transaction['out']:
                    tr = bitcoin_transaction()
                    tr.blockNumber = current_blocknum
                    tr.reciver_address = output["addr"]
                    tr.sender_addresses = input_addr
                    tr.txid = transaction_hash
                    tr.amount = output["value"]
                    tr.save()

            block = block_save(block_height=str(
                current_blocknum), system='bitcoin')
            block.save()

            current_blocknum_obj.btc = current_blocknum_obj.btc + 1
            current_blocknum_obj.save()
            try:
                bitcoin_transaction.objects.filter(
                    blockNumber=current_blocknum-6).delete()
                current_blocknum = current_blocknum + 1
            except Exception as e:
                print(e)
                print('cant delete block number{}'.format(current_blocknum))
        except Exception as e:
            print(e)
