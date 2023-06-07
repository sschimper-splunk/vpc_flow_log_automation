import firehose_flowlogs_utils as utils

firehose_delivery_stream_name = "Splunk"

utils.print_header(delete=False)

regions = utils.get_aws_azs()
for region in regions:
    utils.create_firehose_delivery_stream(region, firehose_delivery_stream_name)
    vpcs = utils.get_vpcs(region)
    for vpc in vpcs:
        utils.create_vpc_low_logs(region, vpc, utils.get_firehose_delivery_stream_arn(region, firehose_delivery_stream_name))

utils.print_footer(delete=False)