namespace cl smartyzed
namespace cpp smartyzed
namespace d smartyzed
namespace dart smartyzed
namespace java smartyzed
namespace php smartyzed
namespace perl smartyzed
namespace haxe smartyzed
namespace netstd smartyzed

/**
 *  API definition for the SmartyzeDetect Detection API Server
 */

## API version
/** API version - follows semantic versioning */
const string API_VERSION = "2.1.0"

## configuration and status
/** Result codes for APIs */
enum ResultCode {
  /** Generic success code */
  SUCCESS = 1,
  /** Generic error code */
  ERR_GENERIC = 2,
  /** API server is busy processing requests */
  ERR_BUSY = 3,
  /** Invalid parameters provided by client */
  ERR_INVALID_REQ = 4,
  /** Detection is unsupported on instance (cpu/mem constraints not met) */
  ERR_UNSUPPORTED = 5,
  /** API server is not activated with a license */
  ERR_NOT_ACTIVATED = 6,
  /** API limit provisioned with license is reached */
  ERR_API_LIMIT = 7,
  /** API server not able to reach internet */
  ERR_NET_FAIL = 8,
}

/** API server initialization request */
struct InitRequest {
  /** License for activation */
  1: string license,
}

/** Detection capabilities of instance where API server is running */
struct DetectionCapability {
  /** Number of possible concurrent detection sessions */
  1: i32 numConcurrentSessions
}

/** API server status */
struct DetectorStatus {
  /** S/W version of the server */
  1: string version,
  /** API version of the server */
  2: string apiVersion,
  /** Initialization status of the server */
  3: ResultCode initStatus,
  /** Detection capability of server instance */
  4: DetectionCapability capability,
  /** Activation challenge for license in offline mode */
  5: string activationChallenge,
}

## settings
/** Object detection accuracy/speed setting */
enum ObjectDetectionEnv {
  /** Higher speed, lower accuracy */
  NORMAL = 1,
  /** Medium speed, medium accuracy */
  BUSY = 2,
  /** Slower speed, higher accuracy */
  VERY_BUSY = 3
}

/** Line cross criteria for line cross settings */
enum LineCrossCriteria {
  /** Line cross from out to in direction, line extends across view */
  LINE_CROSS = 1,
  /** Line cross from out to in direction, crossing across line only */
  LINE_SEGMENT_CROSS = 2,
  /** Line cross from both directions, line extends across view */
  LINE_CROSS_BOTH_DIR = 3,
  /** Line cross from both directions, crossing across line only */
  LINE_SEGMENT_CROSS_BOTH_DIR = 4
}

/** Detection object type */
enum ObjectType {
  PERSON = 1,
}

/** Settings for object detection */
struct ObjectDetectionSettings {
  /** whether object detection is enabled */
  1: required bool enabled,
  /** object detection accuracy/speed setting */
  2: ObjectDetectionEnv env,
  /** object detection type */
  3: ObjectType objectType,
  /** whether to ignore static objects */
  4: bool detectOnlyMovingObjects,
}

/** Object detection area descriptor */
struct DetectionArea {
  /** top left y co-ordinate normalized [0, 1] */
  1: double top,
  /** top left x co-ordinate normalized [0, 1] */
  2: double left,
  /** bottom right y co-ordinate normalized [0, 1] */
  3: double bottom,
  /** bottom right x co-ordinate normalized [0, 1] */
  4: double right,
  /** friendly name of the area */
  5: string name
}

/** Detection area settings */
struct DetectionAreaSettings {
  /** whether object detection within areas only is enabled */
  1: required bool enabled,
  /** list of object detection areas (max of 2) */
  2: list<DetectionArea> areas,
}

/**
 * Normalized co-ordinate descriptor
 * Co-ordinate system: Top left of image is (0,0)
 * x increases from left to right
 * y increases from top to bottom
 */
struct NormPoint {
  /** x co-ordinate normalized [0,1] */
  1: required double x,
  /** y co-ordinate normalized [0,1] */
  2: required double y,
}

/** Social distancing detection settings */
struct SocialDistanceSettings {
  /** whether social distancing violation detection is enabled */
  1: required bool enabled,
  /** 4 points indicating a rectangular area on the ground in view */
  2: list<NormPoint> groundBoundary,
  /** 2 points indicating the minimum separation on the ground */
  3: list<NormPoint> minSeparation,
}

/**
 * Line crossing detection settings
 * Note: A line cross is considered using the bottom middle point
 * of an object bounding box as reference
 */
struct LineCrossSettings {
  /** whether line crossing detection is enabled */
  1: required bool enabled,
  /** 2 points on the ground in view indicating the line to monitor */
  2: list<NormPoint> boundary,
  /** 1 point denoting the 'in' side of the line */
  3: NormPoint inPoint,
  /** Line cross mode to detect */
  4: LineCrossCriteria crossCriteria,
}

/** Mask detection settings */
struct MaskDetectionSettings {
  /** whether mask detection is enabled */
  1: required bool enabled,
}

/** Automatic License Plate Recognition (ALPR) settings */
struct AlprSettings {
  /** whether ALPR is enabled */
  1: required bool enabled,
  /** region code to be used for ALPR */
  2: string region,
  /** whether to skip vehicle check for license plate detection */
  3: bool skipVehicleCheck,
  /** preset mode specifying speed/accuracy tradeoff - default is 'medium' */
  4: string presetMode,
}

/** Detection settings for a session */
struct DetectionSettings {
  /** Object detection settings */
  1: ObjectDetectionSettings objSettings,
  /** Social distancing detection settings */
  2: SocialDistanceSettings sdSettings,
  /** Area detection settings */
  3: DetectionAreaSettings detAreaSettings,
  /** Line cross settings */
  4: LineCrossSettings lineCrossSettings,
  /** Mask detection settings */
  5: MaskDetectionSettings maskSettings,
  /** ALPR settings */
  6: AlprSettings alprSettings,
}

## inputs
/** Detection session descriptor */
struct DetectionSession {
  /** A unique id of the session */
  1: i32 id,
  /** Detection settings for the session */
  2: DetectionSettings detectionSettings,
}

/** Detection input type */
enum DetectionInputType {
  /** Raw image pixel data (e.g., RGB buffer) */
  IMG_BUFFER_RAW = 1,
  /** Encoded image data (e.g., JPEG buffer) */
  IMG_BUFFER_ENCODED = 2,
  /** Path to an image file */
  IMG_FILE_PATH = 3,
  /** Path to a video file */
  VID_FILE_PATH = 4
}

/** Raw image pixel format */
enum ImageBufferFormat {
  /** RGB format in HWC (Height-Width-Channel) order */
  RGB_HWC = 1
}

/** Raw image input */
struct RawImageInput {
  /** width of image */
  1: i16 width,
  /** height of image */
  2: i16 height,
  /** image pixel format */
  3: ImageBufferFormat format,
  /** image buffer */
  4: binary buffer
}

/** Encoded image format type */
enum EncodedImageFormat {
  /** JPEG encoding */
  JPEG = 1
}

/** Encoded image input */
struct EncodedImageInput {
  /** encoding format of image */
  1: EncodedImageFormat format,
  /** encoded image buffer */
  2: binary buffer,
  /** buffer length */
  3: i32 bufferLength,
}

/** Image file based input */
struct ImageFileInput {
  /** path to image file */
  1: string filename,
}

/** Video file based input */
struct VideoFileInput {
  /** path to video file */
  1: string filename,
  /** processing FPS for video (max 10) */
  2: i32 processFps,
}

/** Media input for detection */
union InputParams {
  /** raw pixel image */
  1: RawImageInput rawImageInput,
  /** encoded image */
  2: EncodedImageInput encImageInput,
  /** image file input */
  3: ImageFileInput imgFileInput,
  /** video file input */
  4: VideoFileInput vidFileInput,
}

/** Detection input */
struct DetectionInput {
  /** detection input type */
  1: DetectionInputType type,
  /** detection input params */
  2: InputParams params
}

## outputs
/** Line cross direction */
enum CrossDirection {
  /** direction not determined */
  UNKNOWN = 0,
  /** crossing from out to in */
  CROSS_IN = 1,
  /** crossing from in to out */
  CROSS_OUT = 2,
}

/** Detected object descriptor */
struct DetectedObject {
  /** friendly name of detected object */
  1: string name,
  /** unique object id for object within session */
  2: i32 objectId,
  /** top-left y co-ordinate normalized [0,1] */
  3: double top,
  /** top-left x co-ordinate normalized [0,1] */
  4: double left,
  /** bottom-right y co-ordinate normalized [0,1] */
  5: double bottom,
  /** bottom-right x co-ordinate normalized [0,1] */
  6: double right,
  /** index of frame (for videos) where object was detected */
  7: i32 frameIndex,
  /** confidence score of detection [0, 1] */
  8: double confidence,
  /** line cross direction (if applicable) */
  9: CrossDirection direction,
}

/** Object detection result */
struct ObjectDetectionResult {
  /** list of detected objects */
  1: list<DetectedObject> objects,
}

/** Social distancing violation instance - detected object pair in violation */
struct SocialDistanceViolation {
  1: DetectedObject first,
  2: DetectedObject second,
}

/** Social distancing violation results */
struct SocialDistanceResult {
  /** list of social distancing violations */
  1: list<SocialDistanceViolation> violations,
}

/** Line cross violation instance */
struct LineCrossViolation {
  /** object position before crossing */
  1: DetectedObject first,
  /** object position after crossing */
  2: DetectedObject second,
}

/** Line cross detection results */
struct LineCrossDetectionResult {
  /** list of line cross violations */
  1: list<LineCrossViolation> violations,
}

/** Mask detection results */
struct MaskDetectionResult {
  /** list of mask (violations and compliant) objects */
  1: list<DetectedObject> objects,
}

/** Detected Text descriptor */
struct DetectedText {
  /** detected text in utf-8 encoding */
  1: string text,
  /** top-left y co-ordinate normalized [0,1] */
  2: double topLeftY,
  /** top-left x co-ordinate normalized [0,1] */
  3: double topLeftX,
  /** top-right y co-ordinate normalized [0,1] */
  4: double topRightY,
  /** top-right x co-ordinate normalized [0,1] */
  5: double topRightX,
  /** bottom-right y co-ordinate normalized [0,1] */
  6: double bottomRightY,
  /** bottom-right x co-ordinate normalized [0,1] */
  7: double bottomRightX,
  /** bottom-left y co-ordinate normalized [0,1] */
  8: double bottomLeftY,
  /** bottom-left x co-ordinate normalized [0,1] */
  9: double bottomLeftX,
  /** confidence score of detection [0, 1] */
  10: double confidence,
}

/** License Plate Number descriptor */
struct LicensePlateNumber {
  /** license plate number in utf-8 encoding */
  1: string plate,
  /** confidence of detection [0, 1] */
  2: double confidence,
}

/** License plate descriptor */
struct LicensePlate {
  /** license plate number detections for this plate */
  1: list<LicensePlateNumber> detections,
  /** unique object id for object within session */
  2: i32 objectId,
  /** top-left y co-ordinate normalized [0,1] */
  3: double top,
  /** top-left x co-ordinate normalized [0,1] */
  4: double left,
  /** bottom-right y co-ordinate normalized [0,1] */
  5: double bottom,
  /** bottom-right x co-ordinate normalized [0,1] */
  6: double right,
  /** index of frame (for videos) where object was detected */
  7: i32 frameIndex,
  /** confidence of detection score [0, 1] */
  8: double confidence,
  /** associated text found with license plate */
  9: list<DetectedText> associatedText,
}

/** ALPR results */
struct AlprResult {
  /** list of ALPR detections */
  1: list<LicensePlate> objects,
}

/** Detection output descriptor */
struct DetectionOutput {
  /** Detection status code */
  1: ResultCode status,
  /** object detections */
  2: optional ObjectDetectionResult objDetResult,
  /** social distancing violations */
  3: optional SocialDistanceResult socialDetResult,
  /** line crossing detections */
  4: optional LineCrossDetectionResult lineCrossResult,
  /** mask detections */
  5: optional MaskDetectionResult maskDetResult,
  /** ALPR detections */
  6: optional AlprResult alprResult,
}

/** Detection API */
service DetectionApi {
  // config/status apis
  /** Init API server with license */
  DetectorStatus init(1: InitRequest request),

  /** Get API server status */
  DetectorStatus getStatus(),

  /** Stop API server */
  ResultCode destroy(),

  // session apis
  /** Create new detection session */
  i32 createSession(1: DetectionSettings settings),

  /** Retrieve list of active sessions */
  list<DetectionSession> getSessions(),

  /** Delete an active session */
  ResultCode deleteSession(1: i32 sessionId),

  /** Clear an active session (finalize temporary detections and retrieve output) */
  DetectionOutput clearSession(1: i32 sessionId),

  /** Get output for an active session */
  DetectionOutput getSessionResult(1: i32 sessionId),

  /** Feed input for a detection session (typically used with videos) */
  ResultCode processInputForSession(1: i32 sessionId, 2: i32 frameIndex, 3: DetectionInput input),

  // single call api
  /** Combo API call to run detection and retrieve output in one-shot */
  DetectionOutput runDetection(1: DetectionInput input, 2: DetectionSettings settings),
}

