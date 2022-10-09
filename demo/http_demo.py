import argparse
import os
import sys
import json
import requests
import cv2

HAVE_DISPLAY = 1

class BoxUtils:
  """ bbox is (x1, y1, x2, y2) in norm co-ords """
  @staticmethod
  def bboxNormToAbs(bbox, width, height):
    return (round(bbox[0] * width), round(bbox[1] * height),
        round(bbox[2] * width), round(bbox[3] * height))
  pass

  @staticmethod
  def pointsAbsToNorm(points, width, height):
    normPoints = []
    for p in points:
      normPoints.append((p[0] / width, p[1] / height))
    return normPoints
  pass

  @staticmethod
  def pointPairsNormToAbs(pointPairs, width, height):
    absPoints = []
    for pp in pointPairs:
      absPoints.append((
        (round(pp[0][0] * width), round(pp[0][1] * height)),
        (round(pp[1][0] * width), round(pp[1][1] * height))
        ))
    return absPoints
  pass
pass

def selectArea(imgFile):
  img = cv2.imread(imgFile)
  img = cv2.resize(img, (640, 480), interpolation=cv2.INTER_AREA)
  x, y, w, h = cv2.selectROI('Select area', img)
  return [[x / 640.0, y / 480.0, (x + w) / 640.0, (y + h) / 480.0]]
pass

def drawObjects(img, objects, colorMap={}):
  ih, iw = img.shape[:2]
  for det in objects:
    coords = [det['left'], det['top'], det['right'], det['bottom']]
    color = (0, 255, 0)
    if det['name'] in colorMap:
      color = colorMap[det['name']]
    (x1, y1, x2, y2) = BoxUtils.bboxNormToAbs(coords, iw, ih)
    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
pass

def drawPlates(img, objects):
  ih, iw = img.shape[:2]
  for det in objects:
    coords = [det['left'], det['top'], det['right'], det['bottom']]
    (x1, y1, x2, y2) = BoxUtils.bboxNormToAbs(coords, iw, ih)
    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
    label = det['name']
    textColor = (255, 255, 255)
    fontScale = 0.7
    fontThickness = 2
    font = cv2.FONT_HERSHEY_SIMPLEX

    # For the text background
    # Find space required by the text so that we can put a background
    # with that amount of width.
    (w, h), _ = cv2.getTextSize(label, font, fontScale, fontThickness)
    textPadding = int(h / 2)
    cv2.rectangle(img, (x1, y1 - h - textPadding), (x1 + w, y1),
        (255, 0, 0), -1)
    # Print the text
    cv2.putText(img, label, (x1, y1 - int(textPadding / 2)),
        font, fontScale, textColor, fontThickness)
pass

class ObjectExecutor:
  def __init__(self, host, port, detType, areas):
    self.host = host
    self.port = str(port)
    self.type = detType
    self.areas = areas
  pass

  def executeOnImage(self, imgFile):
    areasArr = []
    for area in self.areas:
      areasArr.append({
        'left': area[0],
        'top': area[1],
        'right': area[2],
        'bottom': area[3]
      })
    settings = {
      'type': self.type,
      'params': {
        'areas': areasArr
      }
    }
    url = 'http://' + self.host + ':' + self.port + '/v1/detect'
    files = {
        'media': ('media', open(imgFile, 'rb')),
        'settings': ('settings', json.dumps(settings))
    }
    res = requests.post(url, files=files)
    if res.status_code != 200:
      print('Api execution failed:', res.status_code)
    else:
      rjson = res.json()
      if rjson['status'] != 1:
        print('Api execution failed with status:', rjson['status'])
        return
      img = cv2.imread(imgFile)
      img = cv2.resize(img, (640, 480), interpolation=cv2.INTER_AREA)
      colorMap = {}
      if self.type == 'mask':
        colorMap = {'none': (0, 0, 255), 'mask': (0, 255, 0)}
      drawObjects(img, rjson['result'][0]['data'], colorMap=colorMap)
      if HAVE_DISPLAY:
        cv2.imshow('Result', img)
        cv2.waitKey(0)
      else:
        cv2.imwrite('result.jpg', img)
        print(rjson['result'][0]['data'])
  pass
pass

class AlprExecutor:
  def __init__(self, host, port, region, skipVehicleCheck, presetMode):
    self.host = host
    self.port = str(port)
    self.region = region
    self.skipVehicleCheck = skipVehicleCheck
    self.presetMode = presetMode
  pass

  def executeOnImage(self, imgFile):
    settings = {
      'type': 'alpr',
      'params': {
        'region': self.region,
        'skipVehicleCheck': 1 if self.skipVehicleCheck else 0,
        'presetMode': self.presetMode
      }
    }
    url = 'http://' + self.host + ':' + self.port + '/v1/detect'
    files = {
        'media': ('media', open(imgFile, 'rb')),
        'settings': ('settings', json.dumps(settings))
    }
    res = requests.post(url, files=files)
    if res.status_code != 200:
      print('Api execution failed:', res.status_code)
    else:
      rjson = res.json()
      #print(rjson)
      if rjson['status'] != 1:
        print('Api execution failed with status:', rjson['status'])
        return
      img = cv2.imread(imgFile)
      img = cv2.resize(img, (640, 480), interpolation=cv2.INTER_AREA)
      drawPlates(img, rjson['result'][0]['data'])
      if HAVE_DISPLAY:
        cv2.imshow('Result', img)
        cv2.waitKey(0)
      else:
        cv2.imwrite('result.jpg', img)
        print(rjson['result'][0]['data'])
  pass
pass

def main():
  # construct the argument parser and parse the arguments
  ap = argparse.ArgumentParser()
  ## api server specific arguments
  ap.add_argument("-s", "--host", type=str,
      help="ip address of api server", required=False,
      default='localhost')
  ap.add_argument("-p", "--port", type=int,
      help="port at api server", required=False,
      default=9090)
  ## media arguments
  ap.add_argument("-i", "--input", type=str,
      help="path to input image file", required=True)
  ap.add_argument("-t", "--type", type=str,
      help="type of detection (object|mask|alpr)", required=False,
      default='alpr')
  ## alpr specific arguments
  ap.add_argument("-r", "--region", type=str,
      help="lpr region parameter (us|generic)", required=False,
      default='generic')
  ap.add_argument('-n', '--skipvehicle', action='store_true',
      help='skip vehicle check for detection',
      required=False, default=False)
  ap.add_argument('-m', '--presetmode',
      help='preset mode for ALPR', type=str,
      required=False, default='medium')
  ## generic arguments
  ap.add_argument("-a", '--area',
      help='select area for detection', action='store_true',
      required=False, default=False)
  args = ap.parse_args()

  if args.input is None or not os.path.isfile(args.input):
    print('Fail::input image is required')
    sys.exit(-1)

  VALID_TYPES = ['object', 'mask', 'alpr']
  if args.type not in VALID_TYPES:
    print('Fail::detection type is required', VALID_TYPES)
    sys.exit(-1)

  areas = []
  if args.area and HAVE_DISPLAY:
    areas = selectArea(args.input)

  if args.type == 'alpr':
    VALID_ALPR_REGIONS = ['us', 'generic']
    if args.region not in VALID_ALPR_REGIONS:
      print('Fail::lpr region is required', VALID_ALPR_REGIONS)
      sys.exit(-1)
    elif args.region == 'generic':
      args.region = '' # generic is empty string for api

    apiExecutor = AlprExecutor(args.host, args.port, args.region,
        args.skipvehicle, args.presetmode)
    apiExecutor.executeOnImage(args.input)
  else:
    apiExecutor = ObjectExecutor(args.host, args.port, args.type, areas)
    apiExecutor.executeOnImage(args.input)
pass

if __name__ == "__main__":
  main()
