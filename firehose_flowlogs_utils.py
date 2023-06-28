import logging
import boto3
from botocore.exceptions import ClientError

#setup simple logging for INFO
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Get the account ID in which the script is executed
def get_caller_identity():
    return boto3.client('sts').get_caller_identity().get('Account')

def log_header(delete):
    account_id = get_caller_identity()
    if(delete):
        print(f"Deleting the following AWS resources for account '{account_id}':")
    else:
        print(f"Creating the following AWS resources for account '{account_id}':")
    print("------------------------------------------------------------------")
    
def log_footer(delete):
    account_id = get_caller_identity()
    if(delete):
        print(f"Deletion completed for account '{account_id}'!")
    else:
        print(f"Creation completed for account '{account_id}'!")

# Get all supported AWS Regions and Availability Zones
def get_aws_azs():
    client = boto3.client("ec2")
    return [region['RegionName'] for region in client.describe_regions()['Regions']]

def create_splunk_flowlogs_processor_lambda(region):
    this_client = boto3.client('serverlessrepo', region_name=region)
    try:
        this_client.create_application(
            Author='Splunk',
            Description='Data transformation function to stream VPC Flowlogs to Splunk via Firehose',
            Name='splunk-firehose-flowlogs-processor',
        )
        print(f"splunk-firehose-flowlogs-processor app created for region {region}")
    except Exception as e:
        print(f"{str(e)} - Skipping creation of splunk-firehose-flowlogs-processor app in region {region} ...")

def delete_splunk_flowlogs_processor_lambda(region):
    this_client = boto3.client('serverlessrepo', region_name=region)
    apps = this_client.list_applications()
    apps = apps['Applications']
    app_id = None
    for app in apps:
        if(app['Name'] == 'splunk-firehose-flowlogs-processor'):
            app_id = app['ApplicationId']
            break
    
    if app_id is None:
        print(f"splunk-firehose-flowlogs-processor app not found ... Skipping deletion. for region {region}...")
        return

    this_client.delete_application(
        ApplicationId = app_id
    )
    print("splunk-firehose-flowlogs-processor app deleted")

# Create Firehose Delivery Stream
def create_firehose_delivery_stream(region, delivery_stream_name, splunk_base_url, splunk_hec_token):
    # create_splunk_flowlogs_processor_lambda(region)
    this_client = boto3.client("firehose", region_name=region)
    try:
        this_client.create_delivery_stream(
                                            DeliveryStreamName=delivery_stream_name,
                                            DeliveryStreamType='DirectPut',
                                            SplunkDestinationConfiguration={
                                                        'HECEndpoint': f'https://{splunk_base_url}:8088/services/collector',
                                                        'HECEndpointType': 'Raw',
                                                        'HECToken': splunk_hec_token,
                                                        'HECAcknowledgmentTimeoutInSeconds': 180,
                                                        'RetryOptions': {
                                                            'DurationInSeconds': 300
                                                        },
                                                        'S3Configuration': {
                                                            'RoleARN': 'arn:aws:iam::029977037364:role/Boto3Role',
                                                            'BucketARN': 'arn:aws:s3:::firehose-splunk-backupd' # hardcoded
                                                        },
                                                         'ProcessingConfiguration': {
                                                            'Enabled': True,
                                                            'Processors': [
                                                                {
                                                                    'Type': 'Lambda',
                                                                    'Parameters': [
                                                                            {
                                                                                'ParameterName' : 'LambdaArn',
                                                                                'ParameterValue' : 'arn:aws:lambda:eu-west-1:029977037364:function:serverlessrepo-splunk-fir-SplunkFirehoseFlowlogsPr-4nPwKXdSMAPs'
                                                                            },
                                                                            {
                                                                                'ParameterName' : 'RoleArn',
                                                                                'ParameterValue' : 'arn:aws:iam::029977037364:role/AdminAccess'
                                                                            },
                                                                            {
                                                                                'ParameterName' : 'BufferSizeInMBs',
                                                                                'ParameterValue' : '1'
                                                                            },
                                                                            {
                                                                                'ParameterName' : 'BufferIntervalInSeconds',
                                                                                'ParameterValue' : '60'
                                                                            }
                                                                    ]
                                                                },
                                                            ]
                                                        }                                                       
                                            }
                                        )
        print(f"Created Kinesis Firehose Delivery Stream called '{delivery_stream_name}' for region {region}")
    except Exception as e:
        print(f"{str(e)} - Skipping creation ...")
        # print(f"Kinesis Firehose DataStream with name {delivery_stream_name} in region {region} already exists. Skipping creation.")
        return

# Delte Firehose Delivery Stream
def delete_firehose_delivery_stream(region, delivery_stream_name):
    # delete_splunk_flowlogs_processor_lambda(region)
    this_client = boto3.client("firehose", region_name=region)
    try:
        this_client.delete_delivery_stream(
                                            DeliveryStreamName=delivery_stream_name,
                                        )
        print(f"Deleted Kinesis Firehose Delivery Stream called {delivery_stream_name} for region {region}")
    except Exception as e:
        print(f"{str(e)} - Skipping deletion of Kinesis Firehose Delivery Stream in region {region} ...")

# Get Firehose Delivery Stream ARN
def get_firehose_delivery_stream_arn(region, name):
    this_client = boto3.client("firehose", region_name=region)
    response = this_client.describe_delivery_stream(
                DeliveryStreamName=name
                )
    info = response.get("DeliveryStreamDescription")
    if info:
        info = info.get("DeliveryStreamARN")
    return info

# Get Flow Log ID for a Flow Log Group connectied to a specific VPC
def get_flow_log_id(region, vpc):
    this_client = boto3.client("ec2", region_name=region)
    describe_flow_logs_response =  this_client.describe_flow_logs(
                                    DryRun=False,
                                    Filters=[
                                        {
                                            'Name': 'resource-id',
                                            'Values': [ vpc["VpcId"] ]
                                        },
                                        ]
                                    )
    flow_logs = describe_flow_logs_response.get("FlowLogs")
    if flow_logs:
        flow_logs = flow_logs.pop()
        return flow_logs.get("FlowLogId")
    return None

# Get a list of all VPCs for a given region
def get_vpcs(region):
    this_client = boto3.client("ec2", region_name=region)
    try:
        paginator = this_client.get_paginator('describe_vpcs')
        response_iterator = paginator.paginate()
        full_result = response_iterator.build_full_result()
        vpc_list = []
        for page in full_result['Vpcs']:
            vpc_list.append(page)
    except ClientError:
        raise
    else:
        return vpc_list
    
# Create VPC Flow Logs for a given VPC in a region 
def create_vpc_low_logs(region, vpc, data_stream_arn):
    this_client = boto3.client("ec2", region_name=region)
    try:
        response = this_client.create_flow_logs(
                                    DryRun=False,
                                    ResourceType='VPC',
                                    TrafficType="ALL",
                                    ResourceIds=[
                                        vpc["VpcId"]
                                    ],
                                    LogDestination=data_stream_arn,
                                    LogDestinationType='kinesis-data-firehose',
                                    MaxAggregationInterval=60,
                                    TagSpecifications=[
                                       {"ResourceType": "vpc-flow-log", "Tags": [{"Key": "Name", "Value": "SplunkVPCFlowFLogs"}]} 
                                    ]
                                    )
        
        vpc_id = vpc["VpcId"]
        flow_log_id = response["FlowLogIds"].pop()
        print(f"Created Flow Logs for VPC {vpc_id} with ID {flow_log_id} for region {region}")
    except Exception as e:
        print(f"{str(e)} - Skipping creation ...")
        return
    
# Delete VPC Flow Logs for a given VPC in a region
def delete_vpc_low_logs(region, vpc):
    this_client = boto3.client("ec2", region_name=region)
    flow_log_id = get_flow_log_id(region, vpc)
    if not flow_log_id:
        return
    try:
        this_client.delete_flow_logs(
                                    DryRun=False,
                                    FlowLogIds = [
                                        flow_log_id
                                    ]
                                    )
        vpc_id = vpc["VpcId"]
        print(f"Deleted Flow Logs for VPC {vpc_id} with ID {flow_log_id} for region {region}")
    except Exception as e:
        print(f"{str(e)} - Skipping deletion for VPC Flow Logs in region {region} ...")