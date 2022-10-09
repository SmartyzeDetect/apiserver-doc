"""
  Use this script to connect to the api server and delete
  existing sessions. This is useful during debugging runs when
  experimenting with the api where sessions may be left
  active without cleanup.
"""

import sys
from DetectionApiClientImpl import DetectionApiClient

DetectionApiClient.waitForServer(host=sys.argv[1])

