import firehose_flowlogs_utils as utils
import splunk_utils as splunk

splunk.splunk_delete_hec("boto3_test")

'''
utils.log_header(delete=True)

firehose_delivery_stream_name = "Splunk"
regions = utils.get_aws_azs()
for region in regions:
    vpcs = utils.get_vpcs(region)
    for vpc in vpcs:
        utils.delete_vpc_low_logs(region, vpc)
    utils.delete_firehose_delivery_stream(region, firehose_delivery_stream_name)

utils.log_footer(delete=True)
'''