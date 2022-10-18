"""
  Use this script to check the usage of lookups for your license.
  You will receive the keys necessary to make the API call when you
  get access to a license.
"""

import requests
from aws_requests_auth.aws_auth import AWSRequestsAuth

auth = AWSRequestsAuth(aws_access_key='YOUR_ACCESS_KEY',
                       aws_secret_access_key='YOUR_SECRET_KEY',
                       aws_host='license.smartyzedetect.com',
                       aws_region='ap-south-1',
                       aws_service='execute-api')

response = requests.get('https://license.smartyzedetect.com/api/license',
                        headers={'x-api-key': 'YOUR_API_KEY'},
                        auth=auth)
print(response.content)

