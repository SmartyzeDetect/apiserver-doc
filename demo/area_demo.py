import argparse
import os
import sys
import pickle

from api.ttypes import *
from DetectionApiClientImpl import DetectionApiClient
from DetectionRunner import DetectionRunner
from utils import DisplayUtils

PROC_FPS = 10

class ApiExecutor:
  def __init__(self, host, port):
    self.client = DetectionApiClient.createClient(
        host=host, port=port)
    self.runner = DetectionRunner(objEnabled=True, maskEnabled=False,
        objEnv=ObjectDetectionEnv.VERY_BUSY)
    self.output = None
  pass

  def setDetectionAreaSettings(self, top, left, bottom, right):
    self.runner.setDetectionAreaSettings(top, left, bottom, right, True)
  pass

  def executeOnVideo(self, video):
    self.output = self.runner.runOnVideoFrames(self.client, video, PROC_FPS)
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

  ## get line cross parameters from user
  (status, points) = DisplayUtils.scanPoints(args.input, 2,
      'Mark top-left and bottom-right of area to monitor')
  if not status:
    print('Fail::detection area points selection failed')
    sys.exit(-2)

  apiExecutor.setDetectionAreaSettings(points[0][1],
      points[0][0], points[1][1], points[1][0])

  res = apiExecutor.executeOnVideo(args.input)
  if not res:
    print('Fail::failed to execute api',
        apiExecutor.getOutput().status)
    sys.exit(-3)

  ## display the results
  output = apiExecutor.getOutput()
  DisplayUtils.showVideoDetections(args.input, PROC_FPS, output,
      plotName='Detections in area')
  if args.output is not None and len(args.output) > 0:
    dataOut = {}
    dataOut['type'] = 'AreaDetection'
    dataOut['input'] = os.path.abspath(args.input)
    dataOut['area'] = points
    dataOut['fps'] = PROC_FPS
    dataOut['output'] = output
    with open(args.output, 'wb') as of:
      pickle.dump(dataOut, of)
pass

if __name__ == "__main__":
  main()
