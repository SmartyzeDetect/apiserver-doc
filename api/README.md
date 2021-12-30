## Introduction

The SmartyzeDetect API server exposes detection APIs via a thrift RPC interface. The [thrift framework](https://thrift.apache.org/) is used for RPC definition and client code generation to enable easy integration. Different API transports are available (TCP socket, Unix socket, etc) and can be configured during API server deployment. Please refer to the documentation under deploy directory for instructions relating to API server configuration. The API server supports AI functions using CPU based inference for ML models. Docker container images are provided for Linux OS on x86-64 architectures and can be run on compatible machines (with support for SSE, AVX and AVX2 instructions).

The API definition is available in api/api.thrift and can be used to generate client calling code in various languages. Steps for client code generation are available at the thrift documentation page [here](https://thrift.apache.org/tutorial/).

## Design

The SmartyzeDetect API provides a high-level interface to AI capabilities. It is designed to abstract away the details of the lower level AI model interactions. It also encapsulates additional capabilities on top of raw AI model inference results which is required for use in real-world usecases including functions like area detection, object tracking, line-cross detection, social distancing detection and algorithms for reducing false positive detections.

## API Activation

To interact with the API, first you will need to initialize the API itself using a license. This is done by means of an activation flow similar to authentication flows. Each instance of a deployed SDK provides an identifier which is used to generate an activation key. The activation key is then supplied back to the SDK to activate it. The SDK needs internet access whereever its deployed so that it can validate the activation key.

![API Activation Sequence!](/assets/images/ActivateSDK.png "Activation")

## Session

The AI functions of the SDK are centered around sessions created using the SDK. A session represents a set of AI detection settings that are applied for every detection processed using that session. Sessions are stateful and each session holds the results of detection applied on input using it. It is useful as a generic concept for processing multiple frames sequentially using the same detection settings. A typical flow for usage of the API would be to create a session with the required detection settings, then process one or more frames using that session and finally retrieve results for that session and delete the session itself in the end. Processing for video streams would typically use this approach.

![Session Usage Sequence!](/assets/images/SessionUsage.png "Session Usage")

## Session Limits

- Concurrency: The number of concurrent sessions available on an SDK instance is limited by the CPU capabilities and memory (RAM) available on the physical machine or VM it runs on. Running multiple SDK instances on the same physical machine or VM is not supported and will cause issues. A single SDK instance is designed to use the full capabilities on the physical machine or VM it runs on. The concurrent sessions limit is primarily a function of number of CPU cores available to the SDK (if memory is not a limiting factor). So for N cores available, (N - 1) concurrent sessions would be supported (provided memory is not a limiting factor).

- Frame Limit: The number of frames that can be processed within a session is limited to 600. Using a session for processing frames beyond this limit will result in an error being returned from the API.

