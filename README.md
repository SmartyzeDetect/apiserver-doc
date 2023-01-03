## SmartyzeDetect API Server

SmartyzeDetect provides simplified APIs for AI-based solutions like ANPR/ALPR, Intrusion Detection, Line-cross Detection (Tripwire), Social Distancing Detection and Mask Detection. The API is deployable as a [Docker](https://www.docker.com/) container and accessible via either a REST or [thrift](https://thrift.apache.org/) RPC interface.

This repository contains a basic user guide for anyone wishing to try out the APIs for themselves. It currently has:
  - A high level conceptual overview of the API
  - The API specification and associated documentation
  - A deployment guide demonstrating how to spin up a API server container instance locally via Docker or on AWS ECS (check the [deploy](/deploy) directory for this)
  - Demo scripts which invoke the API as examples for usage (check the [demo](/demo) directory for this)

### Quick start
To get started quickly to try out demos, use the below steps:
  - Get a free trial license using the page [here](https://www.smartyzedetect.com/pages/sdkfreetrial)
  - Deploy a Docker container instance locally using the deployment guide [here](/deploy/docker/README.md)
  - Try the demo scripts [here](/demo/README.md)

### Useful links
The Docker image is available on Amazon ECR Public at [link](https://gallery.ecr.aws/smartyzedetect/ml/sd-apiserver) and also on Dockerhub at [link](https://hub.docker.com/r/smartyzedetect/sd-apiserver)

For a demo showing the capabilities of the API, visit [link](https://youtu.be/zlnMdlDxsyQ) and [link](https://youtu.be/_sKi-1qHNwU)

To obtain a free trial license for the API server, use this [page](https://www.smartyzedetect.com/pages/sdkfreetrial)

To learn more about SmartyzeDetect, visit [link](https://www.smartyzedetect.com)

