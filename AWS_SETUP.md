# AWS Integration Setup Guide

This guide explains how to set up AWS services for the Smart Irrigation System with automatic fallback to local storage.

## Quick Start (Local Development)

The system works out-of-the-box with local storage. No AWS setup required!

```bash
# Terminal 1 - Backend
cd Code/backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd Code/frontend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run dashboard.py
```

Then open:
- Dashboard: http://localhost:8501
- API Docs: http://localhost:8000/docs

## AWS Setup (Optional)

To enable AWS services, configure your `.env` file and AWS credentials.

### Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured:
   ```bash
   aws configure
   ```
3. **AWS Credentials** in `~/.aws/credentials` or environment variables

### Configuration

Edit `.env` file:

```env
# Enable AWS services
USE_AWS=true
FALLBACK_ENABLED=true
AWS_REGION=us-east-1
```

### AWS Services Setup

#### 1. Amazon Timestream (Sensor Data)

```bash
# Create database
aws timestream-write create-database --database-name irrigation_db

# Create table
aws timestream-write create-table \
  --database-name irrigation_db \
  --table-name sensor_readings \
  --retention-properties MemoryStoreRetentionPeriodInHours=12,MagneticStoreRetentionPeriodInDays=365
```

Update `.env`:
```env
TIMESTREAM_DATABASE=irrigation_db
TIMESTREAM_TABLE=sensor_readings
```

#### 2. Amazon RDS PostgreSQL (Decisions)

```bash
# Create RDS instance (via AWS Console or CLI)
aws rds create-db-instance \
  --db-instance-identifier irrigation-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password YourPassword123 \
  --allocated-storage 20
```

Update `.env`:
```env
RDS_HOST=your-rds-endpoint.rds.amazonaws.com
RDS_PORT=5432
RDS_DATABASE=irrigation_db
RDS_USER=admin
RDS_PASSWORD=YourPassword123
```

Then create the table:
```sql
CREATE TABLE irrigation_decisions (
    decision_id TEXT PRIMARY KEY,
    farmer_id TEXT,
    timestamp TEXT,
    current_moisture REAL,
    forecasted_moisture REAL,
    irrigation_amount REAL,
    alerts TEXT,
    explanation TEXT
);
```

#### 3. Amazon S3 (Model Results)

```bash
# Create S3 bucket
aws s3 mb s3://irrigation-model-results --region us-east-1
```

Update `.env`:
```env
S3_BUCKET=irrigation-model-results
```

#### 4. Amazon SNS (Alerts)

```bash
# Create SNS topic
aws sns create-topic --name irrigation-alerts

# Subscribe to topic (replace with your phone)
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:irrigation-alerts \
  --protocol sms \
  --notification-endpoint +1234567890
```

Update `.env`:
```env
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:ACCOUNT_ID:irrigation-alerts
```

#### 5. Amazon Bedrock (LLM)

1. Go to AWS Console → Bedrock → Model Access
2. Request access to Claude 3 Sonnet
3. Wait for approval (usually instant)

Update `.env`:
```env
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

### IAM Permissions

Create an IAM policy with these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "timestream:WriteRecords",
        "timestream:DescribeTable",
        "timestream:ListTables"
      ],
      "Resource": "arn:aws:timestream:*:*:database/irrigation_db/table/sensor_readings"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::irrigation-model-results",
        "arn:aws:s3:::irrigation-model-results/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": "arn:aws:sns:*:*:irrigation-alerts"
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "arn:aws:bedrock:*:*:foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
    }
  ]
}
```

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Application Layer                      │
│  (app.py, lstm_model.py, rl_model.py, etc.)            │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              AWS Integration Layer                       │
│         (aws_integration.py - Primary)                  │
│  ┌──────────────────────────────────────────────────┐  │
│  │ • Timestream (sensor data)                       │  │
│  │ • RDS PostgreSQL (decisions)                     │  │
│  │ • S3 (model results)                             │  │
│  │ • SNS (notifications)                            │  │
│  │ • Bedrock (LLM explanations)                     │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼ (if AWS fails)          ▼ (if AWS disabled)
┌──────────────────┐      ┌──────────────────┐
│  Local Fallback  │      │  Local Storage   │
│  ┌────────────┐  │      │  ┌────────────┐  │
│  │ CSV files  │  │      │  │ SQLite DB  │  │
│  │ SQLite DB  │  │      │  │ Parquet    │  │
│  │ Parquet    │  │      │  │ Local LLM  │  │
│  │ Local LLM  │  │      │  │ Log files  │  │
│  └────────────┘  │      │  └────────────┘  │
└──────────────────┘      └──────────────────┘
```

### Fallback Logic

1. **Try AWS**: If `USE_AWS=true` and credentials available
2. **Fallback**: If AWS fails or `USE_AWS=false`, use local storage
3. **Logging**: All operations logged with source (AWS or local)

### Status Check

Check AWS service status:

```python
from aws_integration import get_aws_status

status = get_aws_status()
print(status)
# Output:
# {
#   'aws_enabled': True,
#   'fallback_enabled': True,
#   'services': {
#     'timestream': True,
#     'rds': False,
#     's3': True,
#     'sns': False,
#     'bedrock': True
#   }
# }
```

## Troubleshooting

### AWS Credentials Not Found

```bash
# Configure AWS CLI
aws configure

# Or set environment variables
$env:AWS_ACCESS_KEY_ID = "your-key"
$env:AWS_SECRET_ACCESS_KEY = "your-secret"
$env:AWS_REGION = "us-east-1"
```

### Timestream Write Fails

- Check IAM permissions
- Verify database and table exist
- Check retention policies

### RDS Connection Fails

- Verify security group allows inbound on port 5432
- Check credentials in `.env`
- Ensure database and table exist

### S3 Upload Fails

- Check bucket exists and is in correct region
- Verify IAM permissions
- Check bucket policy

### Bedrock Invocation Fails

- Verify model access is enabled in Bedrock console
- Check IAM permissions
- Verify model ID is correct

## Cost Optimization

### Development

- Use local storage (free)
- Enable fallback for safety
- Disable AWS services when not needed

### Production

- Use Timestream for time-series data (pay per write)
- Use RDS for structured data (pay per instance hour)
- Use S3 for model results (pay per GB stored)
- Use SNS for notifications (pay per message)
- Use Bedrock for LLM (pay per token)

### Cost Estimates (Monthly)

- Timestream: ~$0.30 (1M writes)
- RDS: ~$15-30 (t3.micro)
- S3: ~$1-5 (1GB storage)
- SNS: ~$0.50 (1000 messages)
- Bedrock: ~$5-20 (depending on usage)

**Total: ~$20-60/month for production**

## Next Steps

1. Start with local development (no AWS needed)
2. Test with AWS services in development
3. Deploy to production with AWS
4. Monitor costs and optimize

For more information, see:
- [AWS Timestream Documentation](https://docs.aws.amazon.com/timestream/)
- [AWS RDS Documentation](https://docs.aws.amazon.com/rds/)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [AWS SNS Documentation](https://docs.aws.amazon.com/sns/)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
