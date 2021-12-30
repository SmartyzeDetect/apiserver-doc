import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

## name of aws profile to use for deployment commands
AWS_PROFILE_NAME = os.environ.get('AWS_PROFILE_NAME')

## name of ecs cluster
CLUSTER_NAME = os.environ.get('CLUSTER_NAME')

## name of task definition
TASK_FAMILY_NAME = os.environ.get('TASK_FAMILY_NAME')

## name of task definition with version
TASK_FAMILY_NAME_FULL = os.environ.get('TASK_FAMILY_NAME_FULL')

## version qualified name of the image to load into container definition
IMAGE_NAME = os.environ.get('IMAGE_NAME')

## task execution role with permissions to pull container images from ecr
TASK_EXEC_ROLE = os.environ.get('TASK_EXEC_ROLE')

## name of public subnet where fargate task will be launched
SUBNET_NAME = os.environ.get('SUBNET_NAME')

## name of security group applied to fargate task instance
SEC_GROUP_NAME = os.environ.get('SEC_GROUP_NAME')

