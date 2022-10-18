# Demo

The scripts in this directory provide simple demos for the capabilities of the SmartyzeDetect API.

## Pre-requisites

  - In order to run the demo, you need a running instance of the SmartyzeDetect API server (see the deploy directory for instructions to start one).
  - You need a license key to activate the API server before invoking the APIs. You can get one by sending us a request [here](https://www.smartyzedetect.com/sdkfreetrial).
  - You also need python3 and the following pip packages installed:
    - thrift (only if using thrift RPC mode)
    - requests (only if using REST API mode)
    - opencv-python
    - numpy
    - matplotlib
  - You need to run the scripts on a machine with a GUI for viewing detection results and also for certain scripts that need input. You can set the HAVE_DISPLAY variable to 0 in case there is no GUI in which case results will usually be printed to the console output.

## Activation

The first step before running any of the demo scripts is to activate the API using a license. The activate_server.py script is a helper that provides this functionality and can be run as follows. **Note**: If you have deployed the API server with the SD_API_LICENSE_KEY environment variable set, then this step is not required.
```
python3 activate_server.py <server> <port> <license_key>
```
  - requried arguments: 'server' refers to the IP address of the API server and 'port' refers to the TCP port at which API is exposed, 'license_key' is the license key you received from us.

Once activated, you can run any of the demo scripts.

## Running demo scripts

Depending on whether you launched the API server in thrift RPC or REST mode, you will have to run different scripts for the demo.
http_demo.py is used for REST mode, the other `*_demo.py` files are for thrift RPC mode.

All the demo scripts follow a similar input arguments pattern. Every script typically has the following named input arguments that it accepts.
  - host - IP address of the SmartyzeDetect API server (optional, default: 'localhost')
  - port - port of the SmartyzeDetect API server (optional, default: 9090)
  - input - input image/video file path (required)

For example, the person detection script can be invoked as below (this is the thrift RPC version):
```
python3 detection_demo.py --host localhost --port 9090 --input image.jpg
```
The REST demo for ALPR can be invoked as below:
```
python3 http_demo.py --host localhost --port 9090 -t alpr -i image.jpg
```

The demo scripts provided include:
  - detection_demo.py - provides a demo of person detection
  - area_demo.py - provides a demo of person detection within zones
  - linecross_demo.py - provides a demo of line-cross detection
  - socialdist_demo.py - provides a demo of social distancing detection
  - mask_demo.py - provides a demo of the mask violation detection
  - lpr_demo.py - provides a demo of ALPR
  - http_demo.py - provides a demo of ALPR, person detection and mask detection in REST API mode

Some scripts require additional user input for detection settings (for example, area demo needs the zone where person detection should occur and social distancing detection needs configuration of ground plane and distance separation). These require user interaction on a GUI for selecting these settings on an image. You can ofcourse bypass this by setting the values in the scripts and commenting out the user input parts of the demo scripts if you wish (do keep in mind that the values you choose will affect the results).

## Important notes

**Performance: (applicable if using an API server thats deployed remotely) Although some scripts here demonstrate processing video frames using a remote API server, for a production deployment this would not be done because of latency issues inherent in this approach. You should expect higher latencies for the demo scripts themselves especially for videos since each frame needs to be transferred to the API server. In a production deployment scenario, the APIs would be invoked from another cloud service or software running either on the same instance or on the same local network as the API server instance**


