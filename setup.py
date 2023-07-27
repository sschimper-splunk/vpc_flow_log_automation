import firehose_flowlogs_utils as aws
import splunk_utils as splunk

splunk.splunk_create_hec(name="boto3_test", index="main")

'''
firehose_delivery_stream_name = "Splunk"

aws.log_header(delete=False)

regions = aws.get_aws_azs()
for region in regions:
    aws.create_firehose_delivery_stream(region, firehose_delivery_stream_name, splunk_ip, splunk_hec_token)
    vpcs = aws.get_vpcs(region)
    for vpc in vpcs:
        aws.create_vpc_low_logs(region, vpc, aws.get_firehose_delivery_stream_arn(region, firehose_delivery_stream_name))

aws.log_footer(delete=False)
'''