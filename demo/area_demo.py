import argparse
import os
import sys
import pickle

from api.ttypes import *
from DetectionApiClientImpl import DetectionApiClient
from DetectionRunner import DetectionRunner
from utils import DisplayUtils, OutputRenderer

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

  def showFrame(self, frameIndex, frame, sessId, output):
    self.renderer.addOutput(output, frameIndex)
    canContinue = self.renderer.render(frame, frameIndex)
    if not canContinue:
      self.client.deleteSession(sessId)
      sys.exit(0)
  pass

  def executeOnVideo(self, video, displayImm, fixedLines):
    frameCb = None
    if displayImm:
      self.renderer = OutputRenderer(fixedLines=fixedLines,
          plotName='Detections in area')
      frameCb = self.showFrame

    self.output = self.runner.runOnVideoFrames(self.client, video,
        PROC_FPS, frameCb=frameCb)

    succeeded = self.output.status == ResultCode.SUCCESS
    if succeeded and not displayImm:
      DisplayUtils.showVideoDetections(video, PROC_FPS, self.output,
          fixedLines=fixedLines, plotName='Detections in area')
    return succeeded
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
  ap.add_argument('-e', '--end', action='store_true',
    help='show results at end only',
    required=False, default=False)
  args = ap.parse_args()

  if args.input is None or not os.path.isfile(args.input):
    print('Fail::input video path is required')
    sys.exit(-1)

  apiExecutor = ApiExecutor(args.host, args.port)

  ## get area parameters from user
  (status, points) = DisplayUtils.scanPoints(args.input, 2,
      'Mark top-left and bottom-right of area to monitor')
  if not status:
    print('Fail::detection area points selection failed')
    sys.exit(-2)

  apiExecutor.setDetectionAreaSettings(points[0][1],
      points[0][0], points[1][1], points[1][0])

  fixedLines = []
  fixedLines.append(
  (
    (points[0][0], points[0][1]),
    (points[1][0], points[0][1])
  ))
  fixedLines.append(
  (
    (points[0][0], points[0][1]),
    (points[0][0], points[1][1])
  ))
  fixedLines.append(
  (
    (points[1][0], points[0][1]),
    (points[1][0], points[1][1])
  ))
  fixedLines.append(
  (
    (points[0][0], points[1][1]),
    (points[1][0], points[1][1])
  ))

  res = apiExecutor.executeOnVideo(args.input, not args.end, fixedLines)
  if not res:
    print('Fail::failed to execute api',
        apiExecutor.getOutput().status)
    sys.exit(-3)

  output = apiExecutor.getOutput()

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
