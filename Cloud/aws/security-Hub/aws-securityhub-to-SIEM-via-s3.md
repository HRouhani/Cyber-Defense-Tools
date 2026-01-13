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