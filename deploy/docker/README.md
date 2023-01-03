## Prerequisites

To follow the steps in this tutorial, a basic understanding of Docker is required. This tutorial assumes that the following prerequisites have been completed.

1. A Linux machine with Docker (tested with Docker version 20.10.18 on Debian but others should work as well) and access to internet (See Machine Compatibility section at end for compute requirements)

2. A license key for the API server, you can get one by filling out the form at [link](https://www.smartyzedetect.com/pages/sdkfreetrial)

## Deployment

- Step 1: Set the license key that you obtained for the API server in an environment variable

  You can run this in a terminal to do it.
  ```
  export SD_API_LICENSE_KEY="license-key"
  ```

- Step 2: Start API Server

  Start the API server by running the below command in the same terminal. The below command starts the API server in HTTP/REST API mode. You can use different values specified in the below section to enable thrift RPC over TCP.
  ```
  docker run -e SD_API_TRANSPORT=4 -e SD_API_LICENSE_KEY=${SD_API_LICENSE_KEY} -p 127.0.0.1:9090:9090/tcp public.ecr.aws/smartyzedetect/ml/sd-apiserver:latest
  ```

- Step 3: Run the demos

  Once the container is up, you can open up a new terminal window to run the demos. Some samples are provides in the [demo directory](/demo). Once done, you can come back to this window for the cleanup steps.

- Step 4: Clean up

  Run `docker ps` in a terminal to get the name of the running instance and then run `docker stop <name>` to stop the running docker container.

## Configuration

Some behaviors of the API server are configurable by setting certain environment variables. These are listed below and can be configured as needed for your specific deployment scenario.

  **Note that when you change the transport, you also need to adapt the client code that connects to the API server to use the appropriate transport based on the value used here.**

- Environment variable: SD_API_LICENSE_KEY

  Values:
    - <license-key> : License key to use for initializing API server. This can be used to remove explicit initApi calls for license activation and is mandatory for using the HTTP transport


- Environment variable: SD_API_TRANSPORT

  Values:
    - 1 : TCP socket transport (default)
    - 2 : Unix socket transport
    - 4 : HTTP transport - exposes REST API instead of thrift RPC


- Environment variable: SD_API_TCP_PORT

  Values:
    - Range [1026, 65535] : TCP port which the API server should bind to (default is 9090)


- Environment variable: SD_API_TCP_LOCAL

  Values:
    - 0 : API server will bind to selected TCP port on all network interfaces (default)
    - 1 : API server will only bind to selected TCP port on localhost interface (only for thrift RPC, REST API always binds on all network interfaces)

## Machine Compatibility

The SDK requires a host CPU with certain minimum capabilities in order to function. These are listed below in case you are trying to run this on custom hardware or non-cloud environments.
- x86 architecture - CPU
- 64-bit support - CPU & OS
- SSE4.1, AVX and AVX2 instruction support - CPU & OS
- F16C support - CPU
- FMA3 support - CPU

For AWS, it is recommended to run on compute optimized instance types as these are meant for ML inference type workloads (both Intel and AMD CPUs should work - tested on c4, c5 and c5a instance types).

For any custom instance type deployments, please check that the API server can run successfully (launch successfully and successful inference on image/video) before proceeding.

