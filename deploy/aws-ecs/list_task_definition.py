import boto3
from pprint import pprint
from constants import *

session = boto3.Session(profile_name=AWS_PROFILE_NAME)
ecs_client = session.client('ecs')

response = ecs_client.list_task_definitions(
    familyPrefix=TASK_FAMILY_NAME,
    sort='DESC'
)
pprint(response)

