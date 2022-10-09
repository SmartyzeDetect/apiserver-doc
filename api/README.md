## Introduction

The SmartyzeDetect API server provides access to detection APIs either via REST or via thrift RPC (depending on the API transport configuration). The REST API is easy to integrate and can be used for image inputs. Thrift RPC is geared towards multi-frame usecases like line cross detection etc. The [thrift framework](https://thrift.apache.org/) is used for RPC definition and client code generation to enable easy integration. Please refer to the documentation under deploy directory for instructions relating to API server configuration.

The REST API documentation is available [here](https://www.smartyzedetect.com/restapidoc.html). The OpenAPI specification is also available for download from the same page which allows for code generation for clients. There are also code samples provided in the documentation.
The thrift RPC definition is available in api/api.thrift and can be used to generate client calling code in various languages. Steps for client code generation are available at the thrift documentation page [here](https://thrift.apache.org/tutorial/).

## Design

The SmartyzeDetect API provides a high-level interface to AI capabilities. It is designed to abstract away the details of the lower level AI model interactions. It also encapsulates additional capabilities on top of raw AI model inference results which is required for use in real-world usecases including functions like area detection, object tracking, line-cross detection, ANPR/ALPR, social distancing detection and algorithms for reducing false positive detections.

## API Activation

To interact with the API, first you will need to initialize the API itself using a license. The activation sequence is simplified as of version 2.0.0 of the API. It only involves providing the license as an environment variable during deployment or via an API call. The SDK needs internet access whereever its deployed so that it can validate and activate the license.

## Session

The AI functions of the SDK are centered around sessions created using the SDK. A session represents a set of AI detection settings that are applied for every detection processed using that session. Sessions are stateful and each session holds the results of detection applied on input using it. It is useful as a generic concept for processing multiple frames sequentially using the same detection settings. A typical flow for usage of the API would be to create a session with the required detection settings, then process one or more frames using that session and finally retrieve results for that session and delete the session itself in the end. Processing for video streams would typically use this approach. **Note**: The Session API is exposed only via thrift RPC - while the concept exists internally even for REST API, it is not exposed as part of the API itself.

![Session Usage Sequence!](/assets/images/SessionUsage.png "Session Usage")

## Session Limits

- Concurrency: The number of concurrent sessions available on an SDK instance is limited by the CPU capabilities and memory (RAM) available on the physical machine or VM it runs on. Running multiple SDK instances on the same physical machine or VM is not supported and will cause issues. A single SDK instance is designed to use the full capabilities on the physical machine or VM it runs on. The concurrent sessions limit is primarily a function of number of CPU cores (more specifically number of threads) available to the SDK (if memory is not a limiting factor). So for N threads (equivalency to cores will depend on hyperthreading capabilities on the CPU) available, (N - 1) concurrent sessions would be supported (provided memory is not a limiting factor). The correlation between number of sessions and number of threads is also dependent on the type of detection being run within that session. For e.g., object detection and mask detection use 1 thread, however ALPR uses 2 threads. Therefore for ALPR, the minimum number of threads required is 4 and number of concurrent session is (N - 1) / 2 where N is the number of threads available.

- Frame Limit: There is no limit for frames within a session. However only the most recent 600 frame results are retained within a session. The API error due to frame limit within a session is removed as of API version 1.1.0 ~~The number of frames that can be processed within a session is limited to 600. Using a session for processing frames beyond this limit will result in an error being returned from the API.~~

