import argparse
import os
import sys

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
        objEnv=ObjectDetectionEnv.NORMAL)
    self.output = None
  pass

  def setLinecrossSettings(self, boundary, inPoint, crossCriteria):
    self.runner.setLinecrossSettings(boundary, inPoint,
        crossCriteria, True)
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
          plotName='Line Crossings')
      frameCb = self.showFrame

    self.output = self.runner.runOnVideoFrames(self.client, video, PROC_FPS,
        frameCb=frameCb)

    succeeded = self.output.status == ResultCode.SUCCESS
    if succeeded and not displayImm:
      DisplayUtils.showVideoDetections(video, PROC_FPS, self.output,
          fixedLines=fixedLines, plotName='Line Crossings')
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
  ap.add_argument('-e', '--end', action='store_true',
    help='show results at end only',
    required=False, default=False)
  args = ap.parse_args()

  if args.input is None or not os.path.isfile(args.input):
    print('Fail::input video path is required')
    sys.exit(-1)

  apiExecutor = ApiExecutor(args.host, args.port)

  ## get line cross parameters from user
  (status, points) = DisplayUtils.scanPoints(args.input, 3,
      'Mark 2 points for boundary and 1 point inside of boundary')
  if not status:
    print('Fail::line cross points selection failed')
    sys.exit(-2)
  lcBoundary = []
  lcBoundary.append(NormPoint(x=points[0][0], y=points[0][1]))
  lcBoundary.append(NormPoint(x=points[1][0], y=points[1][1]))
  inPoint = NormPoint(x=points[2][0], y=points[2][1])
  apiExecutor.setLinecrossSettings(lcBoundary, inPoint,
      LineCrossCriteria.LINE_CROSS)

  ## fixed line to show boundary
  fixedLines = []
  fixedLines.append((
    (points[0][0], points[0][1]),
    (points[1][0], points[1][1])
  ))

  res = apiExecutor.executeOnVideo(args.input, not args.end,
      fixedLines)
  if not res:
    print('Fail::failed to execute api',
        apiExecutor.getOutput().status)
    sys.exit(-3)
pass

if __name__ == "__main__":
  main()
