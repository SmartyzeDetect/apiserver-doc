import cv2
import sys
import collections
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

HAVE_DISPLAY = 1
DEMO_DELAY = 0 # (ms) set to 0 for wait until key-press

COLOR_PERSON = (255, 0, 0)
COLOR_LC_BEFORE = (0, 255, 0)
COLOR_LC_AFTER = (0, 0, 255)
COLOR_DIST_VIOLATION = (0, 0, 255)
COLOR_NO_MASK = (0, 0, 255)
COLOR_MASK = (0, 255, 0)
COLOR_PLATE = (255, 0, 0)
FIXED_LINE_COLOR = (0, 0, 255)

mousePoints = []

def getMousePoints(event, x, y, flags, param):
  # used to capture mouse clicks on image
  global mousePoints
  if event == cv2.EVENT_LBUTTONDOWN:
    img = param['img']
    cv2.circle(img, (x, y), 10, (0, 255, 255), 10)
    cv2.imshow(param['title'], img)
    mousePoints.append((x, y))
pass

class OutputRenderer:
  def __init__(self, showPersons=True, showLineCross=True,
      showSd=True, showMask=True, showLpr=True, fixedLines=[],
      plotPersons=True, plotLineCross=True, plotSd=True, plotMask=True,
      plotName='Metrics', swapRb=True):
    ## rendering options
    self.showPersons = showPersons
    self.showLineCross = showLineCross
    self.showSd = showSd
    self.showMask = showMask
    self.showLpr = showLpr
    self.plotPersons = plotPersons
    self.plotLineCross = plotLineCross
    self.plotSd = plotSd
    self.plotMask = plotMask
    self.plotName = plotName
    self.fixedLines = fixedLines
    self.swapRb = swapRb
    ## detections by frame
    self.framePersonDets = {}
    self.frameLcBeforeDets = {}
    self.frameLcAfterDets = {}
    self.frameSdDets = {}
    self.frameMaskDets = {}
    self.frameLprDets = {}
    ## accumulate plots
    plotData = []
    plotNames = []
    plotColors = []
    doPlot = plotPersons or plotLineCross or plotSd or plotMask
    self.lineGraph = None
    if doPlot:
      if plotPersons:
        plotData.append(0)
        plotColors.append('#FF0000')
        plotNames.append('person(s)')
      if plotLineCross:
        plotData.append(0)
        plotColors.append('#00FF00')
        plotNames.append('line crossing(s)')
      if plotSd:
        plotData.append(0)
        plotColors.append('#0000FF')
        plotNames.append('distance violation(s)')
      if plotMask:
        ## no mask entries
        plotData.append(0)
        plotColors.append('#0000FF')
        plotNames.append('mask violation(s)')
        ## mask entries
        plotData.append(0)
        plotColors.append('#00FF00')
        plotNames.append('mask(s) detected')
      self.lineGraph = LineGraph(plotName, 10, len(plotData),
          plotNames, plotColors)
    pass
  pass

  def addOutput(self, output, frameIndex):
    ## limit to high confidence detections if required
    CONF_THRESHOLD = 0.0
    for det in output.objDetResult.objects:
      if det.confidence < CONF_THRESHOLD:
        continue
      if det.frameIndex != frameIndex:
        continue
      if det.frameIndex not in self.framePersonDets:
        self.framePersonDets[det.frameIndex] = []
      self.framePersonDets[det.frameIndex].append(det)
    for lcPair in output.lineCrossResult.violations:
      if lcPair.first.confidence < CONF_THRESHOLD or\
          lcPair.second.confidence < CONF_THRESHOLD:
        continue
      if lcPair.first.frameIndex != frameIndex and\
          lcPair.second.frameIndex != frameIndex:
        continue
      if lcPair.second.frameIndex not in self.frameLcBeforeDets:
        self.frameLcBeforeDets[lcPair.second.frameIndex] = []
      self.frameLcBeforeDets[lcPair.second.frameIndex].append(
          lcPair.second)
      if lcPair.first.frameIndex not in self.frameLcAfterDets:
        self.frameLcAfterDets[lcPair.first.frameIndex] = []
      self.frameLcAfterDets[lcPair.first.frameIndex].append(lcPair.first)
    for sdPair in output.socialDetResult.violations:
      if sdPair.first.confidence < CONF_THRESHOLD or\
          sdPair.second.confidence < CONF_THRESHOLD:
        continue
      if sdPair.first.frameIndex != frameIndex:
        continue
      if sdPair.first.frameIndex not in self.frameSdDets:
        self.frameSdDets[sdPair.first.frameIndex] = []
      self.frameSdDets[sdPair.first.frameIndex].append(sdPair.first)
      self.frameSdDets[sdPair.first.frameIndex].append(sdPair.second)
    for det in output.maskDetResult.objects:
      if det.confidence < CONF_THRESHOLD:
        continue
      if det.frameIndex != frameIndex:
        continue
      if det.frameIndex not in self.frameMaskDets:
        self.frameMaskDets[det.frameIndex] = []
      self.frameMaskDets[det.frameIndex].append(det)
    for det in output.alprResult.objects:
      if det.frameIndex != frameIndex:
        continue
      if det.frameIndex not in self.frameLprDets:
        self.frameLprDets[det.frameIndex] = []
      self.frameLprDets[det.frameIndex].append(det)
  pass

  def render(self, frame, frameIndex):
    allDets = []
    allColors = []
    plotData = []
    if self.showPersons:
      numPersons = 0
      if frameIndex in self.framePersonDets:
        pdets = self.framePersonDets[frameIndex]
        for det in pdets:
          allDets.append(det)
          allColors.append(COLOR_PERSON)
        numPersons = len(pdets)
      if self.plotPersons:
        plotData.append(numPersons)

    if self.showLineCross:
      numLineCrossings = 0
      if frameIndex in self.frameLcBeforeDets:
        pdets = self.frameLcBeforeDets[frameIndex]
        for det in pdets:
          allDets.append(det)
          allColors.append(COLOR_LC_BEFORE)
      if frameIndex in self.frameLcAfterDets:
        pdets = self.frameLcAfterDets[frameIndex]
        for det in pdets:
          allDets.append(det)
          allColors.append(COLOR_LC_AFTER)
        numLineCrossings = len(pdets)
      if self.plotLineCross:
        plotData.append(numLineCrossings)

    if self.showSd:
      numSdViolations = 0
      if frameIndex in self.frameSdDets:
        pdets = self.frameSdDets[frameIndex]
        for det in pdets:
          allDets.append(det)
          allColors.append(COLOR_DIST_VIOLATION)
        numSdViolations = len(pdets)
      if self.plotSd:
        plotData.append(int(numSdViolations / 2))

    if self.showMask:
      numNoMasks = 0
      numMasks = 0
      if frameIndex in self.frameMaskDets:
        pdets = self.frameMaskDets[frameIndex]
        for det in pdets:
          allDets.append(det)
          if det.name == "none":
            allColors.append(COLOR_NO_MASK)
            numNoMasks += 1
          else:
            allColors.append(COLOR_MASK)
            numMasks += 1
      if self.plotMask:
        plotData.append(numNoMasks)
        plotData.append(numMasks)

    texts = []
    boxTexts = {}
    if self.showLpr:
      numLprs = 0
      if frameIndex in self.frameLprDets:
        pdets = self.frameLprDets[frameIndex]
        for det in pdets:
          allDets.append(det)
          allColors.append(COLOR_PLATE)
          numLprs += 1
          ## add lpr text to be displayed
          boxTexts[len(allDets) - 1] = det.detections[0].plate
          for i, lp in enumerate(det.detections):
            texts.append('Plate ID({}) #{}:{}'.format(numLprs, i,
                lp.plate))
            if not HAVE_DISPLAY:
              print('Fid({}): Plate ID({}) #{}:{}'.format(frameIndex,
                  numLprs, i, lp.plate))
    pass
 
    simg = None
    ## show metrics graph
    if self.lineGraph is not None:
      self.lineGraph.update(frameIndex, plotData)
      simg = self.lineGraph.render()

    ## show video dets
    texts.append('Frame Index:{}'.format(frameIndex))
    if self.swapRb:
      frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    return DisplayUtils.showFrame(frame, allDets, allColors,
        texts, self.fixedLines, simg, boxTexts=boxTexts)
  pass
pass

class DisplayUtils:
  @staticmethod
  def showFrame(frame, dets, colors, texts, fixedLines, secImg, boxTexts={}):
    (H, W) = frame.shape[:2]
    # draw detection boxes
    for i in range(len(dets)):
      det = dets[i]
      coords = [det.left, det.top, det.right, det.bottom]
      (x1, y1, x2, y2) = BoxUtils.bboxNormToAbs(coords, W, H)
      cv2.rectangle(frame, (x1, y1), (x2, y2), colors[i], 2)
      ## draw any box related texts
      if i in boxTexts:
        textColor = (255, 255, 255)
        label = boxTexts[i]
        fontScale = 0.7
        fontThickness = 2
        font = cv2.FONT_HERSHEY_SIMPLEX

        # For the text background find space required by the text
        # so that we can add a background with same width
        (w, h), _ = cv2.getTextSize(label, font, fontScale, fontThickness)
        textPadding = int(h / 2)
        img = cv2.rectangle(frame, (x1, y1 - h - textPadding), (x1 + w, y1),
            colors[i], -1)
        # Prints the text
        img = cv2.putText(frame, label, (x1, y1 - int(textPadding / 2)),
            font, fontScale, textColor, fontThickness)
      pass
    pass

    # draw any fixed lines
    lines = BoxUtils.pointPairsNormToAbs(fixedLines, W, H)
    for line in lines:
      cv2.line(frame, line[0], line[1], FIXED_LINE_COLOR, 2)
    # draw text sections
    for i in range(len(texts)):
      text = texts[i]
      cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    # combine a secondary image if provided
    if secImg is not None:
      frame = np.hstack((frame, secImg))
    # show the output frame
    if HAVE_DISPLAY:
      cv2.imshow("Frame", frame)
      key = cv2.waitKey(DEMO_DELAY) & 0xFF
      # if the `q` key was pressed, exit the program
      if key == ord("q"):
        return False
        #sys.exit(0)
    else:
      cv2.imwrite('result.jpg', frame)
      if len(dets) > 0:
        print(len(dets), 'detections found')
    return True
  pass

  @staticmethod
  def showVideoDetections(vidFile, fps, output,
      showPersons=True, showLineCross=True, showSd=True,
      showMask=True, showLpr=True, fixedLines=[], plotPersons=True,
      plotLineCross=True, plotSd=True, plotMask=True,
      plotName='Metrics'):

    renderer = OutputRenderer(showPersons, showLineCross, showSd,
        showMask, showLpr, fixedLines, plotPersons,
        plotLineCross, plotSd, plotMask,
        plotName, swapRb=False)

    findex = 0
    vc = cv2.VideoCapture(vidFile)
    if not vc.isOpened():
      print('Fail::failed to open file:', vidFile)
      return False
    vidFps = int(vc.get(cv2.CAP_PROP_FPS))
    frameModulo = max(int(vidFps / fps), 1)

    while True:
      _, frame = vc.read()
      if frame is None:
        break
      if (findex % frameModulo) != 0:
        findex += 1
        continue
      if (findex // frameModulo) >= 600:
        break

      frame = cv2.resize(frame, (640, 480),
          interpolation=cv2.INTER_AREA)
      frameIndex = findex // frameModulo
      renderer.addOutput(output, frameIndex)
      canContinue = renderer.render(frame, frameIndex)
      if not canContinue:
        break

      findex += 1
    pass
    vc.release()
    cv2.destroyAllWindows()
    return True
  pass

  @staticmethod
  def scanPoints(vidFile, numPoints, windowTitle):
    if not HAVE_DISPLAY:
      print('Fail::No display available, cannot select points')
      return (False, [])
    # Get first frame from video
    cap = cv2.VideoCapture(vidFile)
    if not cap.isOpened():
      print('Fail::Video file couldnt be opened:', vidFile)
      return (False, [])

    ret, img = cap.read()
    if not ret:
      print('Fail::Video file reading failed:', vidFile)
      cap.release()
      return (False, [])

    img = cv2.resize(img, (640, 480))

    cv2.namedWindow(windowTitle)
    cv2.setMouseCallback(windowTitle, getMousePoints, {
      'title': windowTitle,
      'img': img,
    })
    cv2.imshow(windowTitle, img)

    while True:
      key = cv2.waitKey(100) & 0xFF
      if key == ord('q'):
        print('User cancelled operation, exiting program')
        sys.exit(0)
      if len(mousePoints) >= numPoints:
        ## add a final wait to ensure final point can be seen
        key = cv2.waitKey(500) & 0xFF
        cv2.destroyWindow(windowTitle)
        break
    cap.release()
    normPoints = BoxUtils.pointsAbsToNorm(mousePoints[:numPoints],
        640, 480)
    return (True, normPoints)
  pass
pass

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

class LineGraph:
  def __init__(self, title, numXDivs, numYAxes, yAxisNames, yAxisColors):
    self.title = title
    self.numXDivs = numXDivs
    self.numYAxes = numYAxes
    self.yAxisNames = yAxisNames
    self.yAxisColors = yAxisColors
    self.yData = []
    for i in range(self.numYAxes):
      self.yData.append(collections.deque(np.zeros(self.numXDivs)))
    self.fig = Figure(figsize=(8, 6), dpi=80) # figsize is inches
    self.canvas = FigureCanvas(self.fig)
  pass

  """
      yAxisData - array with one data point with
      new value per y-axis
  """
  def update(self, xIndex, yAxisData):
    self.updateData(yAxisData)
    self.updateGraph(xIndex)
    self.canvas.draw()
  pass

  def render(self):
    image = np.frombuffer(self.canvas.tostring_rgb(), dtype='uint8')
    image = image.reshape(self.canvas.get_width_height()[::-1] + (3,))
    #cv2.imshow(self.title, image)
    return image
  pass

  def updateData(self, yAxisData):
    for i in range(self.numYAxes):
      self.yData[i].popleft()
      self.yData[i].append(yAxisData[i])
  pass

  def updateGraph(self, xIndex):
    ax = self.fig.gca()
    ## clear axes to start a fresh iteration
    ax.cla()

    maxY = -1
    for i in range(self.numYAxes):
      data = self.yData[i]
      maxY = max(maxY, np.max(self.yData[i]))
      ## plot data line
      ax.plot(data, c=self.yAxisColors[i])
      ## fill area under line
      ax.fill_between(np.arange(len(data)), data,
          color=self.yAxisColors[i], alpha=0.3)
      ## plot last entry alone as a point
      ax.scatter(len(data) - 1, data[-1], c=self.yAxisColors[i])
      ## draw text on top of last point
      if data[-1] > 0:
        ax.text(len(data) - 2, data[-1] + 2,
            "{} {}".format(data[-1], self.yAxisNames[i]))

    ## labeling of axes
    ax.set_xticks(np.arange(-1, self.numXDivs, 2))
    ax.set_xticklabels(np.arange(xIndex - self.numXDivs -1, xIndex, 2))
    ax.set_xlabel('Video Frame')
    ax.margins(x=0)
    ax.set_title(self.title + '\n')
    ax.set_ylim(0, maxY + 2)
    ax.set_ylabel('Number of detections/violations')

    ## remove spines
    ax.spines['left'].set_visible(True)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    ## display grid
    ax.set_axisbelow(True)
    ax.yaxis.grid(linestyle='dashed', alpha=0.8)
  pass
pass
