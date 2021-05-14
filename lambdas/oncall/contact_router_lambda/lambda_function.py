import os
import datetime
import boto3
from boto3.dynamodb.conditions import Key


def lambda_handler(event, context):
    print(event)
    TABLE_NAME = os.environ["TABLE_NAME"]

    on_call_contacts = get_on_call_contacts()

    return on_call_contacts


def get_on_call_contacts():
    nombre_tabla = os.environ["TABLE_NAME"]
    region       = os.environ['REGION']
    ddb_table = boto3.resource('dynamodb', region_name = region).Table(nombre_tabla)

    items = ddb_table.scan()

    on_call = []
    for item in items['Items']:
        if item['oncall'] == True:
            if item['deliveryOptions']['sms']['phoneNumber'] != '':
                on_call.append(item)

    respuesta = {}

    if len(on_call):
        first = on_call[0]
        respuesta['TargetContact'] = '+{}'.format(first['deliveryOptions']['sms']['phoneNumber'])
        respuesta['TargetName'] = '{} {}'.format(first['FirstName'], first['LastName'])
        
        if len(on_call)>1:
            for i in range(1, len(on_call)):
                respuesta[f'TargetContact_{i}'] = '+{}'.format(on_call[i]['deliveryOptions']['sms']['phoneNumber'])
                respuesta[f'TargetName_{i}'] = '{} {}'.format(on_call[i]['FirstName'], on_call[i]['LastName'])
    
    return respuesta