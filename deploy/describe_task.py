import boto3
import sys
import json
from pprint import pprint
from constants import *

session = boto3.Session(profile_name=AWS_PROFILE_NAME)
ecs_client = session.client('ecs')

## First query for tasks under the service
response = ecs_client.list_tasks(
    cluster=CLUSTER_NAME,
)
if len(response['taskArns']) == 0:
  print('Fail::no tasks found for cluster:', CLUSTER_NAME)
  sys.exit(-1)

## for first task, get task details
taskArn = response['taskArns'][0]
response = ecs_client.describe_tasks(
    cluster=CLUSTER_NAME,
    tasks=[
        taskArn,
    ],
)
if len(response['tasks']) == 0:
  print('Fail::no tasks found for cluster:', CLUSTER_NAME)
  sys.exit(-2)

## next parse out the eni ids attached to task
eniIds = []
for task in response['tasks']:
  for attmt in task['attachments']:
    if attmt['type'] != 'ElasticNetworkInterface':
      continue
    for det in attmt['details']:
      if det['name'] == 'networkInterfaceId':
        eniIds.append(det['value'])

if len(eniIds) == 0:
  print('Fail::no network interfaces found for service tasks')
  sys.exit(-3)

## for each eni, get the public ip and display it
ipAddrs = []
ec2_res = session.resource('ec2')
for eniId in eniIds:
  eni = ec2_res.NetworkInterface(eniId)
  ipAddrs.append(eni.association_attribute['PublicIp'])

if len(ipAddrs) == 0:
  print('Fail::no ip addresses found on enis')
  sys.exit(-4)

pprint(ipAddrs)

