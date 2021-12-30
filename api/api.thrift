namespace cl smartyzed
namespace cpp smartyzed
namespace d smartyzed
namespace dart smartyzed
namespace java smartyzed
namespace php smartyzed
namespace perl smartyzed
namespace haxe smartyzed
namespace netstd smartyzed

## API version
const string API_VERSION = "1.0.0"

## configuration and status
enum ResultCode {
  SUCCESS = 1,
  ERR_GENERIC = 2,
  ERR_BUSY = 3,
  ERR_INVALID_REQ = 4,
  ERR_UNSUPPORTED = 5,
  ERR_NOT_ACTIVATED = 6,
}

struct InitRequest {
  1: string license,
}

struct DetectionCapability {
  1: i32 numConcurrentSessions
}

struct DetectorStatus {
  1: string version,
  2: string apiVersion,
  3: ResultCode initStatus,
  4: DetectionCapability capability,
  5: string activationChallenge,
}

## settings
enum ObjectDetectionEnv {
  NORMAL = 1,
  BUSY = 2,
  VERY_BUSY = 3
}

enum LineCrossCriteria {
  LINE_CROSS = 1,
  LINE_SEGMENT_CROSS = 2,
  LINE_CROSS_BOTH_DIR = 3,
  LINE_SEGMENT_CROSS_BOTH_DIR = 4
}

enum ObjectType {
  PERSON = 1,
}

struct ObjectDetectionSettings {
  1: required bool enabled,
  2: ObjectDetectionEnv env,
  3: ObjectType objectType,
  4: bool detectOnlyMovingObjects,
}

struct DetectionArea {
  1: double top,
  2: double left,
  3: double bottom,
  4: double right,
  5: string name
}

struct DetectionAreaSettings {
  1: required bool enabled,
  2: list<DetectionArea> areas,
}

struct NormPoint {
  1: required double x,
  2: required double y,
}

struct SocialDistanceSettings {
  1: required bool enabled,
  2: list<NormPoint> groundBoundary,
  3: list<NormPoint> minSeparation,
}

struct LineCrossSettings {
  1: required bool enabled,
  2: list<NormPoint> boundary,
  3: NormPoint inPoint,
  4: LineCrossCriteria crossCriteria,
}

struct MaskDetectionSettings {
  1: required bool enabled,
}

struct DetectionSettings {
  1: ObjectDetectionSettings objSettings,
  2: SocialDistanceSettings sdSettings,
  3: DetectionAreaSettings detAreaSettings,
  4: LineCrossSettings lineCrossSettings,
  5: MaskDetectionSettings maskSettings,
}

## inputs
struct DetectionSession {
  1: i32 id,
  2: DetectionSettings detectionSettings,
}

enum DetectionInputType {
  IMG_BUFFER_RAW = 1,
  IMG_BUFFER_ENCODED = 2,
  IMG_FILE_PATH = 3,
  VID_FILE_PATH = 4
}

enum ImageBufferFormat {
  RGB_HWC = 1
}

struct RawImageInput {
  1: i16 width,
  2: i16 height,
  3: ImageBufferFormat format,
  4: binary buffer
}

enum EncodedImageFormat {
  JPEG = 1
}

struct EncodedImageInput {
  1: EncodedImageFormat format,
  2: binary buffer,
  3: i32 bufferLength,
}

struct ImageFileInput {
  1: string filename,
}

struct VideoFileInput {
  1: string filename,
  2: i32 processFps,
}

union InputParams {
  1: RawImageInput rawImageInput,
  2: EncodedImageInput encImageInput,
  3: ImageFileInput imgFileInput,
  4: VideoFileInput vidFileInput,
}

struct DetectionInput {
  1: DetectionInputType type,
  2: InputParams params
}

## outputs
enum CrossDirection {
  UNKNOWN = 0,
  CROSS_IN = 1,
  CROSS_OUT = 2,
}

struct DetectedObject {
  1: string name,
  2: i32 objectId,
  3: double top,
  4: double left,
  5: double bottom,
  6: double right,
  7: i32 frameIndex,
  8: double confidence,
  9: CrossDirection direction,
}

struct ObjectDetectionResult {
  1: list<DetectedObject> objects,
}

struct SocialDistanceViolation {
  1: DetectedObject first,
  2: DetectedObject second,
}

struct SocialDistanceResult {
  1: list<SocialDistanceViolation> violations,
}

struct LineCrossViolation {
  1: DetectedObject first,
  2: DetectedObject second,
}

struct LineCrossDetectionResult {
  1: list<LineCrossViolation> violations,
}

struct MaskDetectionResult {
  1: list<DetectedObject> objects,
}

struct DetectionOutput {
  1: ResultCode status,
  2: optional ObjectDetectionResult objDetResult,
  3: optional SocialDistanceResult socialDetResult,
  4: optional LineCrossDetectionResult lineCrossResult,
  5: optional MaskDetectionResult maskDetResult,
}

/** API for the Detection API Server */
service DetectionApi {
  // config/status apis
  DetectorStatus init(1: InitRequest request),

  DetectorStatus getStatus(),

  ResultCode destroy(),

  // session apis
  i32 createSession(1: DetectionSettings settings),

  list<DetectionSession> getSessions(),

  ResultCode deleteSession(1: i32 sessionId),

  DetectionOutput clearSession(1: i32 sessionId),

  DetectionOutput getSessionResult(1: i32 sessionId),

  ResultCode processInputForSession(1: i32 sessionId, 2: i32 frameIndex, 3: DetectionInput input),

  // single call api
  DetectionOutput runDetection(1: DetectionInput input, 2: DetectionSettings settings),
}

