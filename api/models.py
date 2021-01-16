from django.db import models
from django.contrib.auth.models import User
import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from jsonfield import JSONField


class bitcoin_transaction(models.Model):
    blockNumber = models.PositiveIntegerField(null=True)
    sender_addresses = JSONField(null=True)
    reciver_address = models.CharField(max_length=128, null=True)
    amount = models.CharField(max_length=45, null=True)
    txid = models.CharField(max_length=256, null=True)


class Ethereum_Transaction(models.Model):
    blockNumber = models.CharField(max_length=128)
    sender_address = models.CharField(max_length=256, null=True)
    reciver_address = models.CharField(max_length=256, null=True)
    amount = models.CharField(max_length=128)
    txid = models.CharField(max_length=256, null=True)


class Tron_Transaction(models.Model):
    blockNumber = models.CharField(max_length=128)
    sender_address = models.CharField(max_length=256, null=True)
    reciver_address = models.CharField(max_length=256, null=True)
    amount = models.CharField(max_length=128)
    txid = models.CharField(max_length=256, null=True)


class USDT_eth_Transaction(models.Model):
    blockNumber = models.CharField(max_length=128)
    sender_address = models.CharField(max_length=256, null=True)
    reciver_address = models.CharField(max_length=256, null=True)
    amount = models.CharField(max_length=128)
    txid = models.CharField(max_length=256, null=True)

class USDT_trx_Transaction(models.Model):
    blockNumber = models.CharField(max_length=128)
    sender_address = models.CharField(max_length=256, null=True)
    reciver_address = models.CharField(max_length=256, null=True)
    amount = models.CharField(max_length=128)
    txid = models.CharField(max_length=256, null=True)

class DAI_eth_Transaction(models.Model):
    blockNumber = models.CharField(max_length=128)
    sender_address = models.CharField(max_length=256, null=True)
    reciver_address = models.CharField(max_length=256, null=True)
    amount = models.CharField(max_length=128)
    txid = models.CharField(max_length=256, null=True)

class Block_Number(models.Model):
    id_for_filter_object = models.IntegerField()
    trx = models.IntegerField()
    eth = models.IntegerField()
    btc = models.IntegerField()
    usdt_eth = models.IntegerField()
    dai_eth = models.IntegerField()
    usdt_trx = models.IntegerField()

class hook_pre_send(models.Model):
    data = JSONField(null=True)


class block_save(models.Model):
    SYSTEM_CHOICES = (
        ("bitcoin", "bitcoin"),
        ("ethereum", "ethereum"),
        ("tron", "tron"),
        ("usdt_eth", "usdt_eth"),
        ("usdt_dai", "usdt_dai"),
        ("usdt_trx", "usdt_trx")
    )

    block_height = models.CharField(max_length=50, null=False)
    system = models.CharField(
        max_length=10, choices=SYSTEM_CHOICES, null=False, blank=False, )


class Subscribe_table(models.Model):
    system = models.CharField(max_length=64, db_index=True)
    watch_address = models.CharField(max_length=256, unique=True)


def serialize_hook(transaction, system):
    if system == 'bitcoin':
        return {
            'status': 'confirmed',
            'system': 'btc',
            'txid': transaction.txid,
            'sender_addresses': transaction.sender_addresses,
            'reciver_address': transaction.reciver_address,
            'amount': transaction.amount,
        }
    if system == 'ethereum':
        return {
            'status': 'confirmed',
            'system': 'eth',
            'txid': transaction.txid,
            'sender_address': transaction.sender_address,
            'reciver_address': transaction.reciver_address,
            'amount': transaction.amount,
        }
    if system == "tron":
        return {
            'status': 'confirmed',
            'system': 'trx',
            'txid': transaction.txid,
            'sender_address': transaction.sender_address,
            'reciver_address': transaction.reciver_address,
            'amount': transaction.amount,
        }
    if system == 'usdt_eth':
        return {
            'status': 'confirmed',
            'system': 'usdt_eth',
            'txid': transaction.txid,
            'sender_address': transaction.sender_address,
            'reciver_address': transaction.reciver_address,
            'amount': transaction.amount,
        }
    if system == 'usdt_trx':
        return {
            'status': 'confirmed',
            'system': 'usdt_trx',
            'txid': transaction.txid,
            'sender_address': transaction.sender_address,
            'reciver_address': transaction.reciver_address,
            'amount': transaction.amount,
        }

def send_hook(system, block_height):
    try:
        if system == 'bitcoin':
            print('system is bitcoin')
            try:
                system0 = "btc"
                transactions = bitcoin_transaction.objects.filter(
                    blockNumber=block_height)
            except Exception as e:
                print(e)

        elif system == 'ethereum':
            try:
                system0 = 'eth'
                transactions = Ethereum_Transaction.objects.filter(
                    blockNumber=block_height)

            except Exception as e:
                print(e)

        elif system == 'tron':
            try:
                system0 = 'trx'
                transactions = Tron_Transaction.objects.filter(
                    blockNumber=block_height)

            except Exception as e:
                print(e)

        elif system == 'usdt_eth':
            try:
                system0 = 'eth'
                transactions = USDT_eth_Transaction.objects.filter(
                    blockNumber=block_height)

            except Exception as e:
                print(e)
        elif system == 'dai_eth':
            try:
                system0 = 'eth'
                transactions = USDT_eth_Transaction.objects.filter(
                    blockNumber=block_height)

            except Exception as e:
                print(e)
        elif system == 'usdt_trx':
            try:
                system0 = 'trx'
                transactions = USDT_eth_Transaction.objects.filter(
                    blockNumber=block_height)

            except Exception as e:
                print(e)
        for transaction in transactions:
            print(transaction.reciver_address)
            hooks = Subscribe_table.objects.filter(
                system=system0, watch_address=transaction.reciver_address)
            for hook in hooks:
                data = serialize_hook(transaction, system)
                print(data)
                hook_save = hook_pre_send(data=data)
                hook_save.save()
        print('send hook for block {}  finish'.format(block_height))
    except Exception as e:
        print(e)


@receiver(post_save, sender=block_save)
def block_save_signal(sender, instance, created, **kwargs):
    print('post_save')
    print(instance.block_height)
    send_hook(system=instance.system, block_height=instance.block_height)
    instance.delete()
    print('{} delete from block save'.format(instance.block_height))
