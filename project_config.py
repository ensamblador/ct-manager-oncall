import os
import boto3

from  aws_cdk import (
    core,
    aws_lambda
)

from utils.connect import (
    find_instance_id,
    find_source_phone,
    valida_instancia,
    find_prompt_arn,
    get_agent_data,
    find_agent_arn,
    valida_telefono
)

from utils.utils import (
    load_config,
    get_params, 
    get_param
    )

print ("Description: >")
config = load_config('project_params.json')

STACK_NAME = os.environ.get('STACK_NAME')


INSTANCE_ID = get_param(f"/ct-manager/{STACK_NAME}/instance-id")
INSTANCE_ALIAS = get_param(f"/ct-manager/{STACK_NAME}/instance-alias")
SOURCE_PHONE = get_param(f"/ct-manager/{STACK_NAME}/source-phone")
REGION = get_param(f"/ct-manager/{STACK_NAME}/region")
BEEP_PROMPT = get_param(f"/ct-manager/{STACK_NAME}/beep-prompt")
DEFAULT_AGENT =get_param(f"/ct-manager/{STACK_NAME}/default-agent")
PRESIGNED_URL_DURATION = get_param(f"/ct-manager/{STACK_NAME}/presigned-url-duration")


TAGS = config['tags']


SSM_PARAMS = get_params('/ct-manager/{}'.format(STACK_NAME))
assert len(SSM_PARAMS), "No hay parametros previos, asegure de implementar primero el stack base"


client = boto3.client('connect')

if INSTANCE_ID == 'None':
    print(f'Buscando {INSTANCE_ALIAS} en {REGION}')
    INSTANCE_ID = find_instance_id(client, INSTANCE_ALIAS)

if SOURCE_PHONE == 'None':
    print(f'Buscando {INSTANCE_ALIAS} en {REGION}')
    SOURCE_PHONE_LIST = find_source_phone(client, INSTANCE_ID)
    if len(SOURCE_PHONE_LIST):
        SOURCE_PHONE = SOURCE_PHONE_LIST[0]['PhoneNumber']

if BEEP_PROMPT == 'None':
    BEEP_PROMPT = 'Beep.wav'

BEEP_PROMPT_ARN = find_prompt_arn(client, INSTANCE_ID, BEEP_PROMPT)
DEFAULT_AGENT_ARN = find_agent_arn(client, INSTANCE_ID, DEFAULT_AGENT)


#** validación
assert valida_instancia(client, INSTANCE_ID), "No se encuentra Instance Id {} en region {}".format(INSTANCE_ID, REGION)
assert valida_telefono(client, INSTANCE_ID, SOURCE_PHONE), "Se requiere al menos un número de teléfono asociado a la instancia"
assert BEEP_PROMPT_ARN, 'No se encontró el prompt Beep.wav, si utiliza otro cambieen project_params.json'
assert DEFAULT_AGENT_ARN, 'No se encontro el usuario por defecto, revise project_params.json'

DEFAULT_AGENT_DATA = get_agent_data(client, INSTANCE_ID, DEFAULT_AGENT_ARN.split('/')[-1])


REMOVAL_POLICY = core.RemovalPolicy.DESTROY

TTL_METRICS = 365

BASE_LAMBDA_CONFIG = dict (
    timeout=core.Duration.seconds(20),       
    memory_size=256,
    tracing= aws_lambda.Tracing.ACTIVE)

PYTHON_LAMBDA_CONFIG = dict (runtime=aws_lambda.Runtime.PYTHON_3_8, **BASE_LAMBDA_CONFIG)

LAMBDA_JAVA_CONFIG = dict (
    timeout=core.Duration.seconds(900),       
    memory_size=512,
    tracing= aws_lambda.Tracing.ACTIVE,
    runtime=aws_lambda.Runtime.JAVA_8)


BASE_ENV_VARIABLES = dict (INSTANCE_ID = INSTANCE_ID, REGION = REGION, SOURCE_PHONE= SOURCE_PHONE)



BASE_INTEGRATION_CONFIG =  dict(proxy=True,
    integration_responses=[{
        'statusCode': '200',
        'responseParameters': {
            'method.response.header.Access-Control-Allow-Origin': "'*'"
        }
    }])

BASE_METHOD_RESPONSE = dict(
    method_responses=[{
        'statusCode': '200',
        'responseParameters': {
            'method.response.header.Access-Control-Allow-Origin': True,
        }
    }]
)