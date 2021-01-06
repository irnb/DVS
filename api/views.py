from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_api_key.permissions import HasAPIKey

from django.db import IntegrityError

from api.models import Subscribe_table
from .serializers import SubscribeSerializer
class Subscribe(APIView):
    '''
    doc :
    method: post 
    input :
        a) watch_address
        b) system
    output:
        a) ok 200
        b) Bad Request 400
    '''
    permission_classes = [HasAPIKey]
    def post(self, request):
        serializer = SubscribeSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.data
        else:
            return Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json",
            )
        watch_address = data["watch_address"]
        system = data["system"]
        try:
            subscribe = Subscribe_table.objects.create( watch_address=watch_address,system=system)
        except IntegrityError as e:
            response = {
                'status': 'failed',
                'detail': 'subscribe has problem',
            }
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type='application/json')
        message = {'message':'ok'}
        return Response(data=message, status=status.HTTP_200_OK,content_type='aplication/json')