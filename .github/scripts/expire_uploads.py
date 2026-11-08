"""Apply one-day R2 retention and remove expired CSV uploads without logging keys."""
import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import boto3

account = os.environ['CLOUDFLARE_ACCOUNT_ID']
token = os.environ['CLOUDFLARE_API_TOKEN']
bucket = 'food-impact'


def api(path, method='GET', body=None):
    request = Request('https://api.cloudflare.com/client/v4' + path,
                      data=None if body is None else json.dumps(body).encode(),
                      headers={'Authorization': 'Bearer ' + token,
                               'Content-Type': 'application/json'}, method=method)
    try:
        with urlopen(request, timeout=60) as response:
            data = json.load(response)
    except HTTPError as error:
        raise RuntimeError(f'Cloudflare API returned HTTP {error.code}') from None
    if not data.get('success'):
        raise RuntimeError('Cloudflare API request failed')
    return data['result']


path = f'/accounts/{account}/r2/buckets/{bucket}/lifecycle'
rules = api(path).get('rules', [])
rule = {'id': 'expire-uploads-after-one-day', 'enabled': True,
        'conditions': {'prefix': ''},
        'deleteObjectsTransition': {'condition': {'type': 'Age', 'maxAge': 86400}}}
rules = [r for r in rules if r['id'] != rule['id']] + [rule]
api(path, 'PUT', {'rules': rules})
assert rule in api(path)['rules'], 'Lifecycle verification failed'
print('Verified R2 lifecycle: delete objects after one day.', flush=True)

# R2 S3 credentials are derived from the existing API token, kept only in memory.
verified = api('/user/tokens/verify')
s3 = boto3.client('s3', endpoint_url=f'https://{account}.r2.cloudflarestorage.com',
                  region_name='auto', aws_access_key_id=verified['id'],
                  aws_secret_access_key=hashlib.sha256(token.encode()).hexdigest())
cutoff = datetime.now(timezone.utc) - timedelta(days=1)
objects = []
for page in s3.get_paginator('list_objects_v2').paginate(Bucket=bucket):
    objects.extend(page.get('Contents', []))
old = [o for o in objects if o['Key'].startswith('csv-') and o['Key'].endswith('.csv')
       and o['LastModified'] < cutoff]
print(f'Bucket objects: {len(objects)}; expired CSV uploads: {len(old)}.', flush=True)
for offset in range(0, len(old), 1000):
    response = s3.delete_objects(Bucket=bucket, Delete={
        'Objects': [{'Key': o['Key']} for o in old[offset:offset + 1000]], 'Quiet': True})
    if response.get('Errors'):
        raise RuntimeError('Some expired uploads could not be deleted')
remaining = 0
for page in s3.get_paginator('list_objects_v2').paginate(Bucket=bucket, Prefix='csv-'):
    remaining += sum(o['Key'].endswith('.csv') and o['LastModified'] < cutoff
                     for o in page.get('Contents', []))
assert remaining == 0, 'Expired uploads remain'
print(f'Deleted {len(old)} expired CSV uploads; verified none remain.', flush=True)
