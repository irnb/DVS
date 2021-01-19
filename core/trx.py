from django_cron import CronJobBase
from django_cron import Schedule

from api.models import block_save
from api.models import Tron_Transaction
from api.models import Block_Number

import requests
import json


from core.help_config import CONFIG_PATH
from core.help_config import from_hex

with open(CONFIG_PATH) as f:
    config = json.load(f)

tron_api_getBlockByNumber_url = config["tron_api_getBlockByNumber_url"]


class GetTRXBlock(CronJobBase):
    RUN_EVERY_MINS = 1/12

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'get_trx_transaction'

    def do(self):
        start()


def start():
    current_blocknum_obj = Block_Number.objects.filter(
        id_for_filter_object=0)[0]
    current_blocknum = current_blocknum_obj.trx

    last_blocknum = requests.get(config["tron_api_lastBlockNumber_url"])
    last_blocknum = json.loads(last_blocknum.text)[
        "block_header"]["raw_data"]["number"]

    confirm_acceptable_block_num = last_blocknum - 22

    while (confirm_acceptable_block_num > current_blocknum):

        data_dict = {
            "num": current_blocknum
        }

        current_block_temp = requests.post(
            tron_api_getBlockByNumber_url, data=json.dumps(data_dict))
        current_block = json.loads(current_block_temp.text)
        print(current_block)
        succsses = True
        try:
            for transaction in current_block["transactions"]:
                if transaction["raw_data"]["contract"][0]["type"] == "TransferContract":
                    if transaction["ret"][0]["contractRet"] == "SUCCESS":

                        tr = Tron_Transaction()
                        tr.blockNumber = current_block["block_header"]['raw_data']['number']
                        tr.sender_address = str(from_hex(
                            transaction["raw_data"]["contract"][0]["parameter"]["value"]["owner_address"]))[2:-1]
                        tr.reciver_address = str(from_hex(
                            transaction["raw_data"]["contract"][0]["parameter"]["value"]["to_address"]))[2:-1]
                        tr.txid = transaction["txID"]
                        tr.amount = int(
                            transaction["raw_data"]["contract"][0]["parameter"]["value"]["amount"]) / 10 ** 6
                        tr.save()

        except:
            succsses = False
            print("we failed to load raw block")
            Tron_Transaction.objects.filter(
                blockNumber=current_block).delete()
        if succsses:
            print('******new block saved******')
            block = block_save(block_height=str(current_block), system='tron')
            block.save()

            current_blocknum_obj.trx = current_blocknum_obj.trx + 1
            current_blocknum_obj.save()
            current_blocknum = current_blocknum+1
            try:
                print('delete block {} start'.format(current_blocknum-22))
                Tron_Transaction.objects.filter(
                    blockNumber=current_blocknum - 22).delete()
                print('block number {} deleted'.format(current_blocknum-22))
            except Exception as e:
                print('cant delete block number{}'.format(current_blocknum-22))
                print(e)
