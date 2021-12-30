import sys
from DetectionApiClientImpl import DetectionApiClient

def activateServer(server, port, awsProfile=None, apiKey=None):
  res = DetectionApiClient.activateServer(server, port, awsProfile, apiKey)
  if res != 0:
    print('Error::activating server failed with code:', res)
  return res
pass

if __name__ == "__main__":
  if len(sys.argv) != 3 and len(sys.argv) != 5:
    print('Fail::invalid number of arguments.')
    print('Usage: python activate_server.py <server> <port> [awsprofile] [apikey]')
    sys.exit(-1)
  if len(sys.argv) == 3:
    sys.exit(activateServer(sys.argv[1], int(sys.argv[2])))
  else:
    sys.exit(activateServer(sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]))

