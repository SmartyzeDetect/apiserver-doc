# Demo
---

The scripts in this directory provide simple demos for the capabilities of the SmartyzeDetect API.

## Pre-requisites

  - In order to run the demo, you would need a running instance of the SmartyzeDetect API server (see the deploy directory for instructions).
  - You need a license to activate the API server before invoking the APIs. You can get one by sending us a request [here](https://www.smartyzedetect.com/sdkfreetrial).
  - You also need python3 and the following pip packages installed:
    - boto3
    - aws_requests_auth
    - thrift
    - opencv-python
    - numpy
    - matplotlib
  - You need to run the scripts on a machine with a GUI for viewing detection results and also for certain scripts that need input.

## Activation

The first step before running any of the demo scripts is to activate the API using a license. The activate_server.py script is a helper that provides this functionality and can be run as follows.
```
python3 activate_server.py <server> <port> [aws_profile] [aws_api_key]
```
  - requried arguments: 'server' refers to the IP address of the API server and 'port' refers to the TCP port at which API is exposed
  - optional arguments: 'aws_profile' refers to the AWS profile configured with the credentials created for SmartyzeDetect license API access and 'aws_api_key' is the API key provided for the license API. If these are not provided, then the script tries to retrieve these from environment variables 'AWS_PROFILE' and 'AWS_API_KEY' respectively

Once activated, you can run any of the other demo scripts.

## Running demo scripts

All the demo scripts follow a similar input arguments pattern. Every script typically has the following named input arguments that it accepts.
  - host - IP address of the SmartyzeDetect API server (optional, default: 'localhost')
  - port - port of the SmartyzeDetect API server (optional, default: 9090)
  - input - input media file path (required)
  - output - output file path where a pickle of the output is stored (optional)

For example, the person detection script can be invoked as below:
```
python3 detection_demo.py --host localhost --port 9000 --input /tmp/invideo.mp4
```

The demo scripts provided include:
  - detection_demo.py - provides a demo of person detection
  - area_demo.py - provides a demo of person detection within zones
  - linecross_demo.py - provides a demo of line-cross detection
  - socialdist_demo.py - provides a demo of social distancing detection
  - mask_demo.py - provides a demo of the mask violation detection

Some scripts require additional user input for detection settings (for example, area demo needs the zone where person detection should occur and social distancing detection needs configuration of ground plane and distance separation). These require user interaction on a GUI for selecting these settings on an image. You can ofcourse bypass this by setting the values in the scripts and commenting out the user input parts of the demo scripts if you wish (do keep in mind that the values you choose will affect the results).

## Important notes

**Performance: Although the scripts here demonstrate processing video frames using a remote API server, for a typical production deployment this would not be done because of latency issues inherent in this approach. You should expect higher latencies for the demo scripts themselves especially for videos since a lot of frames need to be transferred to the API server. In a production deployment, the APIs would be invoked from another cloud service or program running either on the same instance or on the same local network as the API instance**

**Security: To activate the API, the license retrieval code needs access to AWS credentials and API keys which need to be kept secret. Therefore for a production usecase, do not do this from a machine that does not allow for safe storage of these values**

