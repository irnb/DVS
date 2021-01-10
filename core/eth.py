from django_cron import CronJobBase , Schedule

from api.models import Block_Number
from api.models import Ethereum_Transaction
from api.models import block_save

from core.help_config import CONFIG_PATH

import requests
import json

with open(CONFIG_PATH) as f:
    config = json.load(f)

etherscan_apikey = config["etherscan_apikey"]
class GetETHBlock(CronJobBase):
    RUN_EVERY_MINS = 1/2

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'get_eth_transaction'    # a unique code for 

    def do(self):
        start()


def start():
    current_blocknum_obj = Block_Number.objects.filter(id_for_filter_object=0)[0]
    current_blocknum = current_blocknum_obj.eth

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    last_blocknum = requests.get(config["ethereum_api_lastBlockNumber_url"]+config["etherscan_apikey"],headers = headers)
    last_blocknum = int(json.loads(last_blocknum.text)["result"],16)

    confirm_acceptable_block_num = last_blocknum - 20

    while (confirm_acceptable_block_num > current_blocknum) :
        current_blocknum_hex = hex(current_blocknum)
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        block = (requests.get(config["ethereum_api_getBlockByNumber_url"]+ current_blocknum_hex + '&boolean=true&apikey=' + etherscan_apikey , headers = headers)).json()['result']

        
        try:

            for transaction in block['transactions']:
                value = int(transaction['value'], 16)
                value = str(value)
                
                tr = Ethereum_Transaction()
                tr.blockNumber = current_blocknum
                tr.reciver_address = transaction['to']
                tr.sender_address = transaction['from']
                tr.amount = value
                tr.txid = transaction['hash']
                tr.save()
        except Exception as e:
            print("we failed to load raw block")
            Ethereum_Transaction.objects.filter(blockNumber=current_blocknum).delete()

        print('******new block saved******')

        block = block_save(block_height=str(current_blocknum), system='ethereum')
        
        block.save()
        

        current_blocknum_obj.eth = current_blocknum_obj.eth +1
        current_blocknum_obj.save()
        current_blocknum = current_blocknum + 1 
        try:
            print('delete block {} start'.format(current_blocknum ))
            Ethereum_Transaction.objects.filter(blockNumber=current_blocknum-1).delete()
            print('block number {} deleted'.format(current_blocknum ))
        except:
            print('cant delete block number{}'.format(current_blocknum ))


