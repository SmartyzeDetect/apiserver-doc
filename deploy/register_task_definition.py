import boto3
from pprint import pprint
from constants import *

session = boto3.Session(profile_name=AWS_PROFILE_NAME)
ecs_client = session.client('ecs')

response = ecs_client.register_task_definition(
    family=TASK_FAMILY_NAME,
    networkMode='awsvpc',
    executionRoleArn=TASK_EXEC_ROLE,
    containerDefinitions=[
        {
            'name': 'apiserver',
            'image': IMAGE_NAME,
            'portMappings': [
                {
                    'containerPort': 9090,
                    'hostPort': 9090,
                    'protocol': 'tcp'
                },
            ],
            'essential': True,
            'environment': [
                {
                    'name': 'SD_API_TRANSPORT',
                    'value': '1'  ## 1 - tcp socket, 2 - unix socket
                },
                {
                    'name': 'SD_API_TCP_LOCAL',
                    'value': '0'  ## 0 - bind to all ips, 1 - bind only to localhost ip
                },
            ],
            'mountPoints': [
                {
                    'sourceVolume': 'data',
                    'containerPath': '/var/data',
                    'readOnly': False
                },
            ],
        },
    ],
    volumes=[
        {
            'name': 'data',
        },
    ],
    requiresCompatibilities=[
        'FARGATE',
    ],
    cpu='1024',
    memory='2048',
)
pprint(response)

