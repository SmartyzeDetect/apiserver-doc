import cv2
import os

from api.ttypes import *

class DetectionRunner:
  def __init__(self, objEnabled=True, maskEnabled=True,
                      sdEnabled=False, lcEnabled=False, areaEnabled=False,
                      objEnv=ObjectDetectionEnv.NORMAL):
      objSettings = ObjectDetectionSettings(env=objEnv,
          objectType=ObjectType.PERSON, detectOnlyMovingObjects=False,
          enabled=objEnabled)
      ## Note: the values below are given as examples as
      ## a demonstration of the type of data to be used.
      ## In an actual usecase, you would use values from
      ## the setup environment of the video feed you want
      ## to analyze.
      areas = []
      if areaEnabled:
        areas.append(DetectionArea(top=0.25, left=0.25, bottom=0.75,
                                    right=0.50, name="Zone 1"))
        areas.append(DetectionArea(top=0.25, left=0.50, bottom=0.75,
                                    right=0.75, name="Zone 2"))
      areaSettings = DetectionAreaSettings(areas=areas, enabled=areaEnabled)
      sdBoundary = []
      sdBoundary.append(NormPoint(x=0.25, y=0.25))
      sdBoundary.append(NormPoint(x=0.75, y=0.25))
      sdBoundary.append(NormPoint(x=0.25, y=0.75))
      sdBoundary.append(NormPoint(x=0.75, y=0.75))
      sdSeparation = []
      sdSeparation.append(NormPoint(x=0.25, y=0.25))
      sdSeparation.append(NormPoint(x=0.40, y=0.40))
      sdSettings = SocialDistanceSettings(groundBoundary=sdBoundary,
          minSeparation=sdSeparation, enabled=sdEnabled)
      lcBoundary = []
      lcBoundary.append(NormPoint(x=0.25, y=0.25))
      lcBoundary.append(NormPoint(x=0.25, y=0.50))
      lcPoint = NormPoint(x=0.20, y=0.40)
      lcSettings = LineCrossSettings(boundary=lcBoundary, inPoint=lcPoint,
          crossCriteria=LineCrossCriteria.LINE_CROSS, enabled=lcEnabled)
      maskSettings = MaskDetectionSettings(enabled=maskEnabled)

      self.detSettings = DetectionSettings(objSettings=objSettings,
          sdSettings=sdSettings, detAreaSettings=areaSettings,
          lineCrossSettings=lcSettings, maskSettings=maskSettings)
  pass

  """ new settings will only take effect from next new session """
  def setLinecrossSettings(self, boundary, inPoint,
      crossCriteria, enabled):
    lcSettings = LineCrossSettings(boundary=boundary, inPoint=inPoint,
        crossCriteria=crossCriteria, enabled=enabled)
    self.detSettings.lineCrossSettings = lcSettings
  pass

  """ new settings will only take effect from next new session """
  def setSocialDistancingSettings(self, boundary, minSep, enabled):
    sdSettings = SocialDistanceSettings(groundBoundary=boundary,
        minSeparation=minSep, enabled=enabled)
    self.detSettings.sdSettings = sdSettings
  pass

  """ new settings will only take effect from next new session """
  def setDetectionAreaSettings(self, top, left, bottom, right, enabled):
    areas = []
    if enabled:
      areas.append(DetectionArea(top=top, left=left, bottom=bottom,
                       right=right, name="Zone 1"))
    areaSettings = DetectionAreaSettings(areas=areas, enabled=enabled)
    self.detSettings.detAreaSettings = areaSettings
  pass

  def runOnImage(self, client, image, useFile=True, decode=False):
    if image is None or not os.path.isfile(image):
      print('No input image specified', image)
      output = DetectionOutput()
      output.status = ResultCode.ERR_GENERIC
      return output
    if useFile:
      imgFile = os.path.abspath(image)
      imgInput = ImageFileInput(filename=imgFile)
      detParams = InputParams(imgFileInput=imgInput)
      detInput = DetectionInput(type=DetectionInputType.IMG_FILE_PATH,
                  params=detParams)
    elif not decode:
      with open(image, 'rb') as inFile:
        imgBuffer = inFile.read()
      encInput = EncodedImageInput(format=EncodedImageFormat.JPEG,
                                   buffer=imgBuffer,
                                   bufferLength=len(imgBuffer))
      detParams = InputParams(encImageInput=encInput)
      detInput = DetectionInput(type=DetectionInputType.IMG_BUFFER_ENCODED,
                                params=detParams)
    else:
      frame = cv2.imread(image, cv2.IMREAD_COLOR)
      frame = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_AREA)
      frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
      (height, width) = frame.shape[:2]
      imgBuffer = frame.tobytes()
      rawInput = RawImageInput(width=width, height=height,
                                format=ImageBufferFormat.RGB_HWC,
                                buffer=imgBuffer)
      detParams = InputParams(rawImageInput=rawInput)
      detInput = DetectionInput(type=DetectionInputType.IMG_BUFFER_RAW,
                                params=detParams)
    pass
    output = client.runDetection(detInput, self.detSettings)
    return output
  pass

  def runOnVideo(self, client, video, fps):
    if video is None or not os.path.isfile(video):
      print('No input video specified', video)
      output = DetectionOutput()
      output.status = ResultCode.ERR_GENERIC
      return output
    fps = min(fps, 10)
    vidInput = VideoFileInput(filename=video, processFps=fps)
    detParams = InputParams(vidFileInput=vidInput)
    detInput = DetectionInput(type=DetectionInputType.VID_FILE_PATH,
                              params=detParams)
    output = client.runDetection(detInput, self.detSettings)
    return output
  pass

  def runOnVideoFrames(self, client, video, fps, frameCb=None):
    if video is None or not os.path.isfile(video):
      print('Vf:No input video specified', video)
      output = DetectionOutput()
      output.status = ResultCode.ERR_GENERIC
      return output
    fps = min(fps, 10)
    vc = cv2.VideoCapture(video)

    sessId = client.createSession(self.detSettings)

    if sessId == -1:
      vc.release()
      output = DetectionOutput()
      output.status = ResultCode.ERR_GENERIC
      return output
    vidFps = int(vc.get(cv2.CAP_PROP_FPS))
    frameModulo = max(int(vidFps / fps), 1)
    findex= 0
    while True:
      _, frame = vc.read()
      if frame is None:
        break
      if (findex % frameModulo) != 0:
        findex += 1
        continue
      if (findex // frameModulo) >= 600:
        break
      frame = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_AREA)
      frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
      (height, width) = frame.shape[:2]
      imgBuffer = frame.tobytes()
      rawInput = RawImageInput(width=width, height=height,
                                format=ImageBufferFormat.RGB_HWC,
                                buffer=imgBuffer)
      detParams = InputParams(rawImageInput=rawInput)
      detInput = DetectionInput(type=DetectionInputType.IMG_BUFFER_RAW,
                                params=detParams)

      frameIndex = (findex // frameModulo)
      res = client.processInputForSession(sessId, frameIndex,
          detInput)

      if res != ResultCode.SUCCESS:
        print('Failed processing frame {} with {}' % (findex, res))

      if frameCb is not None:
        ## also get current set of results and inform caller
        sessOut = client.getSessionResult(sessId)
        frameCb(frameIndex, frame, sessId, sessOut)

      findex += 1
    pass

    output = client.clearSession(sessId)
    client.deleteSession(sessId)
    vc.release()
    return output
  pass
pass

