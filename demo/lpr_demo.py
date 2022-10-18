import argparse
import os
import sys

from api.ttypes import *
from DetectionApiClientImpl import DetectionApiClient
from DetectionRunner import DetectionRunner
from utils import DisplayUtils, OutputRenderer

class ApiExecutor:
  def __init__(self, host, port, region, skipVehicleCheck, presetMode):
    self.client = DetectionApiClient.createClient(
        host=host, port=port)
    self.runner = DetectionRunner(objEnabled=False, maskEnabled=False,
        objEnv=ObjectDetectionEnv.NORMAL, lprEnabled=True, lprRegion=region,
        lprSkipVehicleCheck=skipVehicleCheck, lprPresetMode=presetMode)
    self.output = None
    self.renderer = None
  pass

  def showFrame(self, frameIndex, frame, sessId, output):
    self.renderer.addOutput(output, frameIndex)
    canContinue = self.renderer.render(frame, frameIndex)
    if not canContinue:
      self.client.deleteSession(sessId)
      sys.exit(0)
  pass

  def executeOnVideo(self, video, displayImm):
    frameCb = None
    if displayImm:
      self.renderer = OutputRenderer(plotPersons=False, plotLineCross=False,
          plotSd=False, plotMask=False)
      frameCb = self.showFrame

    self.output = self.runner.runOnVideoFrames(self.client, video, 5,
        frameCb=frameCb)

    succeeded = self.output.status == ResultCode.SUCCESS
    if succeeded and not displayImm:
      DisplayUtils.showVideoDetections(video, 5, self.output,
          plotName='ALPR')
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
  ap.add_argument("-r", "--region", type=str,
    help="lpr region parameter (us|generic)", required=False,
    default='us')
  ap.add_argument('-n', '--skipvehicle', action='store_true',
    help='skip vehicle check for license plate detection',
    required=False, default=False)
  ap.add_argument('-m', '--presetmode',
    help='preset mode for ALPR (medium|fast)', type=str,
    required=False, default='medium')
  args = ap.parse_args()

  if args.input is None or not os.path.isfile(args.input):
    print('Fail::input video path is required')
    sys.exit(-1)

  VALID_ALPR_REGIONS = ['us', 'generic']
  if args.region not in VALID_ALPR_REGIONS:
    print('Fail::valid lpr region is required (us | generic)')
    sys.exit(-1)
  elif args.region == 'generic':
    args.region = '' # generic is empty string for api

  apiExecutor = ApiExecutor(args.host, args.port, args.region,
      args.skipvehicle, args.presetmode)
  res = apiExecutor.executeOnVideo(args.input, not args.end)
  if not res:
    print('Fail::failed to execute api',
        apiExecutor.getOutput().status)
    sys.exit(-2)
pass

if __name__ == "__main__":
  main()
