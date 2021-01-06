from rest_framework import serializers

NETWORK_CHOICES = (("btc", "btc"), ("eth", "eth"), ("trx", "trx"))


class SubscribeSerializer(serializers.Serializer):
    watch_address = serializers.CharField(required=True, allow_null=False)
    system = serializers.ChoiceField(
        choices=NETWORK_CHOICES, required=True, allow_null=False
    )
