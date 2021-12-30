import argparse
import os
import sys
import pickle

from api.ttypes import *
from DetectionApiClientImpl import DetectionApiClient
from DetectionRunner import DetectionRunner
from utils import DisplayUtils

class ApiExecutor:
  def __init__(self, host, port):
    self.client = DetectionApiClient.createClient(
        host=host, port=port)
    self.runner = DetectionRunner(objEnabled=False, maskEnabled=True,
        objEnv=ObjectDetectionEnv.NORMAL)
    self.output = None
  pass

  def executeOnVideo(self, video):
    self.output = self.runner.runOnVideoFrames(self.client, video, 5)
    return self.output.status == ResultCode.SUCCESS
  pass

  def getOutput(self):
    return self.output
  pass
pass

def main():
  # construct the argument parser and parse the arguments
  ap = argparse.ArgumentParser()
  ap.add_argument("-i", "--input", type=str,
    help="path to input video file", required=True)
  ap.add_argument("-s", "--host", type=str,
    help="ip address of api server", required=False,
    default='localhost')
  ap.add_argument("-p", "--port", type=int,
    help="port at api server", required=False,
    default=9090)
  ap.add_argument("-o", "--output", type=str,
    help="path to output pickle file", required=False,
    default='')
  args = ap.parse_args()

  if args.input is None or not os.path.isfile(args.input):
    print('Fail::input video path is required')
    sys.exit(-1)

  apiExecutor = ApiExecutor(args.host, args.port)
  res = apiExecutor.executeOnVideo(args.input)
  if not res:
    print('Fail::failed to execute api',
        apiExecutor.getOutput().status)
    sys.exit(-2)

  ## display the result
  output = apiExecutor.getOutput()
  DisplayUtils.showVideoDetections(args.input, 5, output,
      plotName='Mask Violations')
  if args.output is not None and len(args.output) > 0:
    dataOut = {}
    dataOut['type'] = 'MaskDetection'
    dataOut['input'] = os.path.abspath(args.input)
    dataOut['fps'] = 5
    dataOut['output'] = output
    with open(args.output, 'wb') as of:
      pickle.dump(dataOut, of)
pass

if __name__ == "__main__":
  main()
