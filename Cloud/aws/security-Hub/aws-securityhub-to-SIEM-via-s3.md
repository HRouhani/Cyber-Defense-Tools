**AWS Security Hub Findings Export to S3**

This guide provides a complete, end-to-end solution for exporting AWS Security Hub findings (aggregated from services like GuardDuty, Inspector, Macie, and Cloud Security Posture Management or CSPM) to an Amazon S3 bucket. From there, the findings can be ingested into another SIEM solution if needed. This setup is particularly useful in a multi-account environment where Security Hub is delegated to a central account.

The solution focuses on streaming real-time findings (new and updated) using Amazon EventBridge and Amazon Kinesis Data Firehose, with an optional section for historical/backfill exports. I'll explain each component in detail, including why it's needed, how it works, and implementation steps. 

**Why This Solution?**

- Security Hub Aggregation: Security Hub centralizes findings from multiple AWS services and accounts. Exporting to S3 creates an audit trail and enables integration with external tools like QRadar/Splunk.
- S3 as Intermediate Storage: S3 is durable, scalable, and cost-effective for storing JSON findings. 
- Real-Time vs. Batch: Streaming handles ongoing findings; batch covers historical data.
- Cost: Low—EventBridge (~$1/million events), Firehose (~$0.029/GB ingested), S3 (~$0.023/GB/month).
- Security: Use IAM least-privilege roles, encryption, and private access.


**Architecture Overview**


Here's a simple diagram (render in GitHub with Mermaid or ASCII art):

```
[Security Hub Findings (GuardDuty, Inspector, Macie, CSPM)]
          |
          v
[EventBridge Rule] --> [Kinesis Data Firehose Delivery Stream]
          |                           |
          v                           v
      (Triggers on imports)       (Buffers & delivers to S3)
                                       |
                                       v
                                 [S3 Bucket]
```

- EventBridge: Captures finding import events.
- Firehose: Buffers data (e.g., every 60s or 1MB) and writes to S3 in partitioned JSON.
- S3: Stores findings for audit and ingestion.


**Step 1: Create an S3 Bucket for Findings**

S3 stores the exported JSON findings securely. Partitioning (e.g., by date/account) makes querying easier and optimizes costs with lifecycle policies.
How it Works: Firehose writes batched JSON objects to S3 paths like findings/year=2026/month=01/day=13/. Enable encryption and logging for compliance.

Implementation:

1. In AWS Console: Go to S3 > Create bucket.
- Name: e.g., security-hub-findings-[your-account-id]-[region] (unique globally).
- Region: Match your Security Hub region (e.g., eu-central-1 for Europe).
- Block public access: Enable all.
- Encryption: SSE-S3 (default) or SSE-KMS for stricter control.
- Versioning: Enable for audit trails.


2. Via AWS CLI:
```
aws s3api create-bucket --bucket security-hub-findings-[your-account-id]-[region] --region eu-central-1 --create-bucket-configuration LocationConstraint=eu-central-1
aws s3api put-bucket-encryption --bucket security-hub-findings-[your-account-id]-[region] --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
aws s3api put-bucket-versioning --bucket security-hub-findings-[your-account-id]-[region] --versioning-configuration Status=Enabled
```

3. Bucket Policy: Allow Firehose writes

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"Service": "firehose.amazonaws.com"},
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::security-hub-findings-[your-account-id]-[region]/*",
      "Condition": {"StringEquals": {"s3:x-amz-acl": "bucket-owner-full-control"}}
    }
  ]
}
```

To Apply via CLI: 

```
aws s3api put-bucket-policy --bucket [bucket-name] --policy file://policy.json
```

Best Practices: Set lifecycle rules to transition to Glacier after 90 days for cost savings. Enable access logging to another bucket.



**Step 2: Create Kinesis Data Firehose Delivery Stream**

Firehose buffers EventBridge events and reliably delivers them to S3. It handles retries, compression, and optional transformations. EventBridge pushes finding events to Firehose, which aggregates them (e.g., 64KB-4MB buffer) and writes compressed JSON to S3.

Implementation:

1. In AWS Console: 

- Go to Kinesis > Amazon Data Firehose > Create delivery stream (data stream).
- Source: Direct PUT (for EventBridge).
- Transformation: Optional—enable and select a Lambda function if you need to filter (e.g., by severity) or format data.
- Destination: Amazon S3.
  Bucket: Select your bucket from Step 1.
  Prefix: findings/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/hour=!{timestamp:HH}/ (dynamic partitioning).
  Error prefix: errors/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/!{firehose:error-output-type}

  important: New line delimiter → set to Enabled

- Buffer hints: Size 1 MiB, Interval 60s (adjust for volume).
- Compression: GZIP (reduces storage).
- Encryption: Enable if using KMS.
- Permissions: Create new IAM role (auto-generated with firehose_delivery_role prefix).

2. Via AWS CLI (example script—save as create-firehose.sh):

```
#!/bin/bash
BUCKET=security-hub-findings-[your-account-id]-[region]
STREAM_NAME=security-hub-findings-stream

aws firehose create-delivery-stream \
  --delivery-stream-name $STREAM_NAME \
  --delivery-stream-type DirectPut \
  --s3-destination-configuration \
    RoleARN=arn:aws:iam::[account-id]:role/firehose_delivery_role \
    BucketARN=arn:aws:s3:::$BUCKET \
    Prefix='findings/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/hour=!{timestamp:HH}/' \
    ErrorOutputPrefix='errors/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/!{firehose:error-output-type}' \
    BufferingHints='{ "SizeInMBs": 1, "IntervalInSeconds": 60 }' \
    CompressionFormat=GZIP
```

Best Practices: Monitor with CloudWatch metrics (e.g., DeliveryToS3.Success). If high volume, increase buffer size.




**Step 3: Create EventBridge Rule**

EventBridge detects Security Hub events in real-time and routes them to Firehose.
The rule matches "Security Hub Findings - Imported" events (includes creates/updates from all sources). In a delegated setup, it captures aggregated findings.

Implementation:

1. In AWS Console: 

- Go to EventBridge > Rules > Create rule.
- Name: SecurityHubFindingsToFirehose.
- Event pattern:

```
{
  "source": ["aws.securityhub"],
  "detail-type": ["Security Hub Findings - Imported"],
  "detail": {
    "findings": {
      "RecordState": ["ACTIVE"],
      "Severity": { "Label": ["HIGH", "CRITICAL"] },
      "Workflow": { "Status": ["NEW", "NOTIFIED"] }
    }
  }
}

```

This is the same filtering style AWS shows in their Security Blog examples (they even recommend including NEW + NOTIFIED). [https://aws.amazon.com/blogs/security/how-to-set-up-and-track-slas-for-resolving-security-hub-findings/]


- Target: Kinesis Firehose stream from Step 2.
- Permissions: Create new IAM role (auto-generated).


2. Via AWS CLI (script create-eventbridge-rule.sh):

```
#!/bin/bash
RULE_NAME=SecurityHubFindingsToFirehose
STREAM_ARN=arn:aws:firehose:[region]:[account-id]:deliverystream/security-hub-findings-stream

aws events put-rule \
  --name $RULE_NAME \
  --event-pattern '{"source":["aws.securityhub"],"detail-type":["Security Hub Findings - Imported"]}'

aws events put-targets \
  --rule $RULE_NAME \
  --targets "Id"="1","Arn"="$STREAM_ARN","RoleArn"="arn:aws:iam::[account-id]:role/eventbridge_role"
```

