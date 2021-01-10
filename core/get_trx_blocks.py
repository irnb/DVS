from django_cron import CronJobBase, Schedule

from api.models import block_save
from api.models import Tron_Transaction
from api.models import Block_Number

import requests
import json
    
from tronapi import Tron 



with open('/etc/DVS-config.json') as f:
    config = json.load(f)

tron_api_getBlockByNumber_url = config["tron_api_getBlockByNumber_url"]

tron = Tron()
class GetTRXBlock(CronJobBase):
    RUN_EVERY_MINS = 1/10

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'get_trx_transaction'   

    def do(self):
        start()
        


def start():
    current_blocknum_obj = Block_Number.objects.filter(id_for_filter_object=0)[0]
    current_blocknum = current_blocknum_obj.trx

    
    confirm_blocknum = current_blocknum - 22
    print(confirm_blocknum)

    data_dict = {
        "num" : confirm_blocknum
    }

    current_block_temp = requests.post(tron_api_getBlockByNumber_url,data = json.dumps(data_dict))
    current_block = json.loads(current_block_temp.text)
    print(current_block)
    try :
        for transaction in current_block["transactions"]:
            if transaction["raw_data"]["contract"][0]["type"] == "TransferContract" :
                if transaction["ret"][0]["contractRet"] == "SUCCESS":
                    
                    tr = Tron_Transaction ()
                    tr.blockNumber = current_block["block_header"]['raw_data']['number']
                    tr.sender_address = str(tron.address.from_hex(transaction["raw_data"]["contract"][0]["parameter"]["value"]["owner_address"]))[2:-1]
                    tr.reciver_address= str(tron.address.from_hex(transaction["raw_data"]["contract"][0]["parameter"]["value"]["to_address"]))[2:-1]
                    tr.txid = transaction["txID"]
                    tr.amount = tron.fromSun(transaction["raw_data"]["contract"][0]["parameter"]["value"]["amount"])
                    tr.save()

    except:
        print("we failed to load raw block")
        Tron_Transaction.objects.filter(blockNumber=confirm_blocknum).delete()

    print('******new block saved******')
    block = block_save(block_height=str(confirm_blocknum), system='tron')
    block.save()

    current_blocknum_obj.trx = current_blocknum_obj.trx + 1 
    current_blocknum_obj.save()
    try:
        print('delete block {} start'.format(confirm_blocknum ))
        Tron_Transaction.objects.filter(blockNumber=confirm_blocknum ).delete()
        print('block number {} deleted'.format(confirm_blocknum ))
    except Exception as e:
        print('cant delete block number{}'.format(confirm_blocknum ))
        print(e)

    