from django.contrib import admin

from api.models import Block_Number
from api.models import DAI_eth_Transaction
from api.models import bitcoin_transaction
from api.models import Ethereum_Transaction
from api.models import Tron_Transaction
from api.models import Subscribe_table
from api.models import USDT_trx_Transaction
from api.models import USDT_eth_Transaction
from api.models import hook_pre_send
from api.models import block_save

class SubscribeTable (admin.ModelAdmin):
    list_display = ('system','watch_address')

admin.site.register(Subscribe_table,SubscribeTable)

admin.site.register(Block_Number)

class Hooks (admin.ModelAdmin):
    list_display = ('is_send',)

admin.site.register(hook_pre_send,Hooks)