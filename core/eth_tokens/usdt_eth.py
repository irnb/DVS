from django_cron import CronJobBase
from django_cron import Schedule

from api.models import Block_Number
from api.models import USDT_eth_Transaction
from api.models import block_save

from core.help_config import CONFIG_PATH
from core.help_config import usdt_eth_abi

import requests
import json

from web3 import Web3, HTTPProvider
from web3.auto import w3


with open(CONFIG_PATH) as f:
    config = json.load(f)

etherscan_apikey = config["etherscan_apikey"]


class GetUSDTBlock(CronJobBase):
    RUN_EVERY_MINS = 1/4

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'get_usdt_eth_transaction'    # a unique code for

    def do(self):
        start()


def start():
    current_blocknum_obj = Block_Number.objects.filter(
        id_for_filter_object=0)[0]
    current_blocknum = current_blocknum_obj.usdt_eth

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    last_blocknum = requests.get(
        config["ethereum_api_lastBlockNumber_url"]+config["etherscan_apikey"], headers=headers)
    last_blocknum = int(json.loads(last_blocknum.text)["result"], 16)

    confirm_acceptable_block_num = last_blocknum - 20

    web3 = Web3(Web3.HTTPProvider(config["eth_node"]))
    contract = web3.eth.contract(
        config["usdt_eth_contract_address"], abi=usdt_eth_abi)

    while (confirm_acceptable_block_num > current_blocknum):
        transfer_events = contract.events.Transfer()
        filter_builder = transfer_events.build_filter()
        filter_builder.fromBlock = current_blocknum
        filter_builder.toBlock = current_blocknum
        filter_instance = filter_builder.deploy(web3)
        transfer_data = filter_instance.get_all_entries()
        transfer_data = Web3.toJSON(transfer_data)
        transfer_data = json.loads(transfer_data)
        
        succsses = True

        try:
            for transaction in transfer_data:

                value = transaction['args']['value'] / (10 ** config["usdt_eth_decimal"])
                value = str(value)

                tr = USDT_eth_Transaction
                tr.blockNumber = current_blocknum
                tr.reciver_address = transaction['args']['to']
                tr.sender_address = transaction['args']['from']
                tr.amount = value
                tr.txid = transaction['transactionHash']
                tr.save()
        except Exception as e:
            succsses = False
            print("we failed to load raw block")
            USDT_eth_Transaction.objects.filter(
                blockNumber=current_blocknum).delete()

        if succsses :
            print('******new block saved******')

            block = block_save(block_height=str(
                current_blocknum), system='usdt')

            block.save()

            current_blocknum_obj.eth = current_blocknum_obj.eth + 1
            current_blocknum_obj.save()
            current_blocknum = current_blocknum + 1
            try:
                print('delete block {} start'.format(current_blocknum))
                USDT_eth_Transaction.objects.filter(
                    blockNumber=current_blocknum-20).delete()
                print('block number {} deleted'.format(current_blocknum))
            except:
                print('cant delete block number{}'.format(current_blocknum))
