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
    self.runner = DetectionRunner(objEnabled=True, maskEnabled=False,
        objEnv=ObjectDetectionEnv.NORMAL)
    self.output = None
  pass

  def setSocialDistanceSettings(self, boundary, separation):
    self.runner.setSocialDistancingSettings(boundary, separation, True)
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

  ## get line cross parameters from user
  (status, points) = DisplayUtils.scanPoints(args.input, 6,
      'Mark 4 points for ground square and 2 points for separation')
  if not status:
    print('Fail::social distance points selection failed')
    sys.exit(-2)
  sdBoundary = []
  sdBoundary.append(NormPoint(x=points[0][0], y=points[0][1]))
  sdBoundary.append(NormPoint(x=points[1][0], y=points[1][1]))
  sdBoundary.append(NormPoint(x=points[2][0], y=points[2][1]))
  sdBoundary.append(NormPoint(x=points[3][0], y=points[3][1]))
  separation = []
  separation.append(NormPoint(x=points[4][0], y=points[4][1]))
  separation.append(NormPoint(x=points[5][0], y=points[5][1]))
  apiExecutor.setSocialDistanceSettings(sdBoundary, separation)

  res = apiExecutor.executeOnVideo(args.input)
  if not res:
    print('Fail::failed to execute api',
        apiExecutor.getOutput().status)
    sys.exit(-3)

  ## display the results
  output = apiExecutor.getOutput()
  DisplayUtils.showVideoDetections(args.input, 5, output,
      plotName='Social Distance Violations')
  if args.output is not None and len(args.output) > 0:
    dataOut = {}
    dataOut['type'] = 'SocialDistDetection'
    dataOut['input'] = os.path.abspath(args.input)
    dataOut['boundary'] = sdBoundary
    dataOut['separation'] = separation
    dataOut['fps'] = 5
    dataOut['output'] = output
    with open(args.output, 'wb') as of:
      pickle.dump(dataOut, of)
pass

if __name__ == "__main__":
  main()
