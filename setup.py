import firehose_flowlogs_utils as utils

firehose_delivery_stream_name = "Splunk"
regions = utils.get_aws_azs()

for region in regions:
    if(region != "eu-west-1"):
        continue

    vpcs = utils.get_vpcs(region)

    for vpc in vpcs:
        utils.create_firehose_delivery_stream(region, firehose_delivery_stream_name)
        utils.create_vpc_low_logs(region, vpc, utils.get_firehose_delivery_stream_arn(region, firehose_delivery_stream_name))
