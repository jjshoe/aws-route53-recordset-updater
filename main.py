import boto3
import json
import os
import requests
import time

import pprint
pp = pprint.PrettyPrinter(indent=4)

client = boto3.client('route53')

hosted_zone_id=os.environ['HOSTED_ZONE_ID']
resource_record_set=os.environ['RESOURCE_RECORD_SET']

def get_current_public_ip():
  endpoint = 'https://ipinfo.io/json'
  response = requests.get(endpoint, verify = True)

  if response.status_code != 200:
    return 'Status:', response.status_code, 'Problem with the request. Exiting.'
    exit()

  data = response.json()

  return data['ip']

def get_current_aws_ip():
  paginator = client.get_paginator('list_resource_record_sets')
  page_iterator = paginator.paginate(HostedZoneId=hosted_zone_id)
  for page in page_iterator:
    for record_set in page['ResourceRecordSets']:
      if record_set['Name'] == resource_record_set:
        for record in record_set['ResourceRecords']:
          return record['Value']

def update_aws_ip(current_public_ip):
  response = client.change_resource_record_sets(
    HostedZoneId=hosted_zone_id,
    ChangeBatch={
      'Changes': [
        {
          'Action': 'UPSERT',
          'ResourceRecordSet': {
            'Name': resource_record_set,
            'Type': 'A',
            'TTL': 60,
            'ResourceRecords': [
              {
                'Value': current_public_ip
              }
            ]
          }
        }
      ]
    }
  )

  print(response)
  change_id = response['ChangeInfo']['Id']
  return change_id

def wait_for_change(change_id):
  timeout = 300  # 5 minutes
  start_time = time.time()
  while time.time() - start_time < timeout:
    response = client.get_change(Id=change_id)
    print(response)
    if response['ChangeInfo']['Status'] == 'INSYNC':
      return
    time.sleep(5)
  print("Timeout waiting for change to complete")
  exit(1)

current_public_ip=get_current_public_ip()
current_aws_ip=get_current_aws_ip()

if current_public_ip != current_aws_ip:
  print('Current IP', current_public_ip, 'does not match the AWS IP', current_aws_ip)
  print('Updating...')
  change_id = update_aws_ip(current_public_ip)
  wait_for_change(change_id)
  print('Done.')
else:
  print('Your current IP matches the AWS IP')
