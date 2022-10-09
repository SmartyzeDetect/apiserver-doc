import sys

from DetectionApiClientImpl import DetectionApiClient

if len(sys.argv) == 1:
  host = '127.0.0.1'
else:
  host = sys.argv[1]

client = DetectionApiClient.createClient(host=host)
res = client.getStatus()
print(res)

