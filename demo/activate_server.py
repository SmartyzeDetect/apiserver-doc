import sys

from api.ttypes import *
from DetectionApiClientImpl import DetectionApiClient

def activateServer(server, port, licenseKey):
  if len(licenseKey) == 0:
    print('Error::License key is empty')
    return -1

  client = DetectionApiClient.createClient(host=server, port=port)
  res = client.getStatus()
  if res.initStatus != ResultCode.ERR_NOT_ACTIVATED:
    client.close()
    if res.initStatus == ResultCode.SUCCESS:
      ## We just return as is here since no activation is required
      print('Success:ApiServer already activated')
      return 0
    print('Error::ApiServer invalid status:', res)
    return -2

  res = client.init(licenseKey)
  #print('License check status:', res)
  client.close()

  if res.initStatus != ResultCode.SUCCESS:
    print('Error::Activation failed:', res)
    return -5

  print('Success::Activation success')
  return 0
pass

if __name__ == "__main__":
  if len(sys.argv) != 4:
    print('Fail::invalid number of arguments.')
    print('Usage: python activate_server.py <server> <port> <licensekey>')
    sys.exit(-1)
  sys.exit(activateServer(sys.argv[1], int(sys.argv[2]), sys.argv[3]))

