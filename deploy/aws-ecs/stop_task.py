import boto3
import sys
from pprint import pprint
from constants import *

session = boto3.Session(profile_name=AWS_PROFILE_NAME)
ecs_client = session.client('ecs')

## First query for tasks under the service
response = ecs_client.list_tasks(
    cluster=CLUSTER_NAME,
)
taskLen = len(response['taskArns'])
if taskLen == 0:
  print('no tasks found for cluster:', CLUSTER_NAME)
  sys.exit(-1)
elif taskLen > 1:
  print('more than 1 task in cluster:', CLUSTER_NAME, taskLen)
  print('Only stopping first one')
pass

## for first task, get task details
taskArn = response['taskArns'][0]

response = ecs_client.stop_task(
    cluster=CLUSTER_NAME,
    task=taskArn,
    reason='CleaningUp'
)

pprint(response)

