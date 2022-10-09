import boto3
from pprint import pprint
from constants import *

session = boto3.Session(profile_name=AWS_PROFILE_NAME)
ecs_client = session.client('ecs')

response = ecs_client.run_task(
    cluster=CLUSTER_NAME,
    count=1,
    enableECSManagedTags=True,
    enableExecuteCommand=False,
    launchType='FARGATE',
    networkConfiguration={
        'awsvpcConfiguration': {
            'subnets': [
                SUBNET_NAME,
            ],
            'securityGroups': [
                SEC_GROUP_NAME,
            ],
            'assignPublicIp': 'ENABLED'
        }
    },
    propagateTags='TASK_DEFINITION',
    referenceId='apiserver-demo',
    startedBy='apiserver-demo',
    taskDefinition=TASK_FAMILY_NAME_FULL
)

pprint(response)

