## Prerequisites

**Note: This demo will use AWS resources and you will incur charges on your AWS account as a result of it. Please be aware of this before continuing**

To follow the steps in this tutorial, a basic understanding of AWS and Amazon ECS concepts is required. This tutorial assumes that the following prerequisites have been completed.

1. The steps in [Setting up with Amazon ECS](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/get-set-up-for-amazon-ecs.html) have been completed.

2. Your AWS user has the required permissions specified in the [Amazon ECS guide here](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/security_iam_id-based-policy-examples.html#first-run-permissions).

3. You have a VPC and security group created to use. This tutorial uses a container image hosted on Amazon ECR, so your task must have internet access. To give your task a route to the internet, use one of the following options.

   - Use a private subnet with a NAT gateway that has an elastic IP address.

   - Use a public subnet and assign a public IP address to the task.

   For more information, see [Creating a VPC with Public and Private Subnets for Your Clusters](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/create-public-private-vpc.html).

   Internet access is also required for the container to validate licenses at runtime.

4. Ensure that the security group created has an incoming rule for tcp traffic allowed on port 9090.  
**Note: This type of configuration is being used for demonstration purposes. In a production usecase, the apiserver container port should not be exposed to the public internet. DO NOT use this configuration in production**

5. Install python3 and boto3 as per [AWS documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html)

6. Create an ECS task execution role that will be needed for pulling container images. See guide [here for instructions](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_execution_IAM_role.html)

## Deployment

For all the deployments the below scripts are going to be using AWS profile based configuration for region and credentials (please refer to the above boto3 guide for how to set this up or for other possible configuration methods that might suit your usecase)

All the steps below require customization according to your deployment environment - including cluster names, task definition, subnet ids, AWS role ARNs etc. All of these are loaded from environment variables in constants.py for convenience. For IMAGE_NAME parameter, ensure that you use the value 'public.ecr.aws/j6h6k0h7/ml/sd-apiserver:latest'

- Step 1: Create a Cluster

  Create your own cluster with a unique name with the following command.
  ```
  python3 create_cluster.py
  ```
  Verify using the below command that the newly created cluster is in the 'active' status.
  ```
  python3 describe_clusters.py
  ```

- Step 2: Register a Task Definition

  Next register the task definition for the API server container with the below command.
  ```
  python3 register_task_definition.py
  ```
  Confirm with the below command that the task definition is listed and available. You should see a taskArn entry in the output response.
  ```
  python3 list_task_definition.py
  ```

- Step 3: Start a task

  Now you will start an instance of the task by using the runTask API from ECS.
  ```
  python3 run_task.py
  ```

- Step 4: Describe the Running Task

  You can check if the new task is launched with the below command. It will list a taskArn in the output.
  ```
  python3 list_tasks.py
  ```

  Once the new task moves to running state, you can retrieve the public IP of the task using the below command. This will be required to invoke the APIs for the rest of the demo.
  ```
  python3 describe_task.py
  ```

- Step 5: Try out the sample demos

  At this point you have a task launched with the apiserver container with a public IP. You can now use the sample demo scripts to try out the APIs. Switch to the demo folder to try out the various usecases. Once done come back here to proceed with cleanup of resources.

  **Note: The deployment above creates a task that will run forever. This will continue incurring charges on your AWS account if not stopped and cleaned up. Remember to clean up the task and cluster once you are done**

- Step 6: Clean up

  Stop the running task using the below command.
  ```
  python3 stop_task.py
  ```
  Verify that all tasks have been shutdown by checking the output of below command. You should see an empty 'taskArns' array in the response.
  ```
  python3 list_tasks.py
  ```
  Once all tasks are stopped, you can delete the cluster itself.
  ```
  python3 delete_cluster.py
  ```

## Configuration

Some behaviors of the API server are configurable by settings certain environment variables. These are listed below and can be configured as needed for your specific deployment scenario.

  **Note that when you change the transport, you also need to adapt the client code that connects to the API server to use the appropriate transport based on the value used here.**

- Environment variable: SD_API_TRANSPORT

  Values:
    - 1 : TCP socket transport
    - 2 : Unix socket transport (Default)


- Environment variable: SD_API_TCP_PORT

  Values:
    - Range [1026, 65535] : TCP port which the API server should bind to (default is 9090)


- Environment variable: SD_API_TCP_LOCAL

  Values:
    - 0 : API server will bind to selected TCP port on all network interfaces
    - 1 : API server will only bind to selected TCP port on localhost interface (default)


- Environment variable: SD_DEBUG_CRASH (WIP)

  Values:
    - 0 : No crash handlers will be setup and no minidump will be generated on API server crash (default)
    - 1 : Crash handlers will be setup and minidump will be written to /var/data/ (make sure this path is mapped to a volume that is writable from within the container and presists after the container exits so that you can retrieve the minidump file)

## Machine Compatibility

The SDK requires a host CPU with certain minimum capabilities in order to function. These are listed below in case you are trying to run this on custom hardware or non-cloud environments.
- 64-bit architecture - CPU & OS
- SSE4.1, AVX and AVX2 instruction support - CPU & OS
- F16C support - CPU
- FMA3 support - CPU

The example above uses Fargate for deploying the API server which works because Fargate for x86 runs on x86-64 based Intel CPUs which have the required CPU capabilities.

For AWS, it is recommended to run on compute optimized instance types as these are meant for ML inference type workloads (both Intel and AMD CPUs should work - tested on c4, c5 and c5a instance types).

For any custom instance type deployments, please check that the API server can run successfully (launch successfully, valid status from getStatus API and successful inference on image/video) before proceeding.

