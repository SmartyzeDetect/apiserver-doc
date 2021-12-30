import boto3
from pprint import pprint
from constants import *

session = boto3.Session(profile_name=AWS_PROFILE_NAME)
ecs_client = session.client('ecs')

response = ecs_client.describe_clusters(clusters=[CLUSTER_NAME])
pprint(response)

