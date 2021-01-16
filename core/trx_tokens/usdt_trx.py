from django_cron import CronJobBase
from django_cron import Schedule

from api.models import block_save
from api.models import USDT_trx_Transaction
from api.models import Block_Number

import requests
import json

from tronapi import Tron
from tronapi import HttpProvider

from core.help_config import CONFIG_PATH

with open(CONFIG_PATH) as f:
    config = json.load(f)

tron_api_getBlockByNumber_url = config["tron_api_getBlockByNumber_url"]


tron = Tron()


class GetTRXBlock(CronJobBase):
    RUN_EVERY_MINS = 1/12

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'get_usdt_trx_transaction'

    def do(self):
        start()


def start():
    current_blocknum_obj = Block_Number.objects.filter(
        id_for_filter_object=0)[0]
    current_blocknum = current_blocknum_obj.usdt_trx

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
                if transaction["raw_data"]["contract"][0]["type"] == "TriggerSmartContract":
                    if transaction["ret"][0]["contractRet"] == "SUCCESS":
                        if tron.address.from_hex(transaction["contract"][0]["contract_address"]) == config["usdt_trx_contract_address"]:
                            txid = transaction["txID"]
                            data = tron.get_event_transaction_id(txid)
                            data = data[0]
                            tr = USDT_trx_Transaction()
                            tr.blockNumber = current_block["block_header"]['raw_data']['number']
                            tr.sender_address = str(tron.address.from_hex(
                                transaction["raw_data"]["contract"][0]["parameter"]["value"]["owner_address"]))[2:-1]
                            tr.reciver_address = str(tron.address.from_hex(
                                str(41)+data['result']['to'][2:]))[2:-1]

                            tr.txid = transaction["txID"]
                            tr.amount = int(data['result']['value'])/10 ** config["usdt_trx_decimal"]
                            tr.save()

        except:
            succsses = False
            print("we failed to load raw block")
            USDT_trx_Transaction.objects.filter(
                blockNumber=current_block).delete()
        if succsses:
            print('******new block saved******')
            block = block_save(block_height=str(current_block), system='usdt_trx')
            block.save()

            current_blocknum_obj.trx = current_blocknum_obj.trx + 1
            current_blocknum_obj.save()
            current_blocknum = current_blocknum+1
            try:
                print('delete block {} start'.format(current_blocknum-22))
                USDT_trx_Transaction.objects.filter(
                    blockNumber=current_blocknum - 22).delete()
                print('block number {} deleted'.format(current_blocknum-22))
            except Exception as e:
                print('cant delete block number{}'.format(current_blocknum-22))
                print(e)
