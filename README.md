# AWS Route53 RecordSet Updater
This script was largely written to keep route53 up to date with my home machine's ever changing IP address

### Usage
I highly recommend running it as a cron. The script takes no command line arguments.

It requires the following environment variables:

* `HOSTED_ZONE_ID` - The Zone ID of the record you want to keep updated
* `RESOURCE_RECORD_SET` - The domain, ending in a '.', that you want to keep up to date

### Authentication
The sciript uses boto3 and supports all the usual authentication methods as the AWS CLI

### Permissions
This script only uses two AWS Rotue53 API calls:
1) `ListResourceRecordSets`
1) `ChangeResourceRecordSets`

A minimum viable AWS IAM policy looks like:

```
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Action": "route53:ChangeResourceRecordSets",
			"Condition": {
				"ForAllValues:StringEquals": {
					"route53:ChangeResourceRecordSetsNormalizedRecordNames": "home.deport.me"
				}
			},
			"Effect": "Allow",
			"Resource": "arn:aws:route53:::hostedzone/yourzoneid"
		},
		{
			"Action": "route53:ListResourceRecordSets",
			"Effect": "Allow",
			"Resource": "arn:aws:route53:::hostedzone/yourzoneid"
		}
	]
}
```
