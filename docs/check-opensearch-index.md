# How to Check if OpenSearch Index Exists

## ⚠️ VPC Access Issue

**If browser access fails**: Your OpenSearch domain is deployed in a VPC private subnet, so direct browser access from outside the VPC is blocked by security groups. Use the methods below instead.

## Index Name
**Default Index**: `turbine-documents`

## Method 1: CloudWatch Logs (Easiest - No VPC Access Needed) ✅

Check if the document processor Lambda successfully created the index:

1. Go to [CloudWatch Logs Console](https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups)
2. Find log group: **`/aws/lambda/solaris-poc-document-processor`**
3. Click on the log group, then on the most recent log stream
4. Search for (use the search box):
   - `"Creating index turbine-documents"`
   - `"Successfully created index turbine-documents"`
   - `"Index turbine-documents already exists"`
   - `"stored.*chunks"` (to see how many chunks were indexed)

**Look for log entries like**:
```
[INFO] Creating index turbine-documents
[INFO] Successfully created index turbine-documents
[INFO] Stored 15 chunks in OpenSearch
```

### Quick CLI Check:

```bash
aws logs filter-log-events \
  --log-group-name /aws/lambda/solaris-poc-document-processor \
  --filter-pattern "index OR stored" \
  --profile mavenlink-functions \
  --region us-east-1 \
  --max-items 20 \
  --query 'events[*].message' \
  --output text | grep -i "index\|stored" | tail -10
```

## Method 2: Use Lambda to Check Index (Recommended for VPC)

Since Lambda has VPC access, we can create a simple check function or use the existing agent workflow Lambda:

### Option A: Invoke Agent Workflow Lambda (Tests RAG)

```bash
# This will try to query OpenSearch via the agent workflow Lambda
aws lambda invoke \
  --function-name solaris-poc-agent-workflow \
  --payload '{"query": "test", "session_id": "check-index"}' \
  --profile mavenlink-functions \
  --region us-east-1 \
  /tmp/response.json

cat /tmp/response.json | jq
```

If index exists and has data, you'll get a response. If index doesn't exist, you'll see an error.

### Option B: Create a Simple Check Script (Run from EC2/Bastion or Lambda)

If you have access to an EC2 instance in the same VPC, or can temporarily create one:

```python
import boto3
import requests
from requests.auth import HTTPBasicAuth
import os

opensearch_endpoint = "your-endpoint.us-east-1.es.amazonaws.com"
username = "admin"
password = os.environ.get("OPENSEARCH_PASSWORD", "TempP@ssw0rd123!Ch@ngeInProd")

# Check if index exists
response = requests.get(
    f"https://{opensearch_endpoint}/turbine-documents",
    auth=HTTPBasicAuth(username, password),
    verify=False  # For self-signed certs in VPC
)

if response.status_code == 200:
    print("✅ Index exists!")
    print(response.json())
elif response.status_code == 404:
    print("❌ Index does not exist")
else:
    print(f"⚠️ Error: {response.status_code}")
    print(response.text)
```

## Method 3: Modify Security Group (Temporary - For Testing Only)

**⚠️ Security Warning**: Only do this temporarily for testing, then remove the rule.

1. Go to [EC2 Console → Security Groups](https://console.aws.amazon.com/ec2/v2/home?region=us-east-1#SecurityGroups:)
2. Find the security group for OpenSearch (should be something like `VectorStoreStack-OpenSearchSecurityGroup-xxxxx`)
3. Click **"Edit inbound rules"**
4. Add a rule:
   - Type: HTTPS
   - Protocol: TCP
   - Port: 443
   - Source: **Your IP address** (use `https://checkip.amazonaws.com` to get it)
   - Description: "Temporary - Check index"
5. Save rules
6. Now try browser access again
7. **⚠️ IMPORTANT**: Remove this rule after checking!

### Get Your IP:

```bash
curl https://checkip.amazonaws.com
```

## Method 4: OpenSearch Dashboards (If Security Group Allows)

**Note**: This only works if security group allows your IP or you're connected via VPN/bastion.

### Step 1: Access OpenSearch Dashboards

1. Go to [AWS OpenSearch Service Console](https://console.aws.amazon.com/es/home?region=us-east-1)
2. Click on your domain: **`solaris-poc-vector-store`**
3. Click the **"OpenSearch Dashboards URL"** link (or "Dashboard URL")
   - URL format: `https://your-domain.us-east-1.es.amazonaws.com/_dashboards`
4. Login with:
   - **Username**: `admin`
   - **Password**: `TempP@ssw0rd123!Ch@ngeInProd` (or your configured password)

### Step 2: Check Index in Dev Tools

1. In OpenSearch Dashboards, click the **hamburger menu** (☰) in the top left
2. Navigate to **"Management"** → **"Dev Tools"** (or use the left sidebar)
3. In the console, run:
   ```json
   GET /_cat/indices?v
   ```
   Or to check a specific index:
   ```json
   GET /turbine-documents
   ```
4. You should see:
   - **Index exists**: Returns index settings and mappings
   - **Index doesn't exist**: Returns `404 Not Found`

### Step 3: View Index Data (Optional)

To see actual documents in the index:
```json
GET /turbine-documents/_search
{
  "size": 10
}
```

## Method 2: AWS Console - OpenSearch Service

### Direct Domain Access

1. Go to [OpenSearch Service Console](https://console.aws.amazon.com/es/home?region=us-east-1)
2. Click on **`solaris-poc-vector-store`** domain
3. Scroll down to **"Domain status"** section
4. Copy the **"Domain endpoint"** (e.g., `search-solaris-poc-vector-store-xxxxx.us-east-1.es.amazonaws.com`)

### Use Browser/curl to Check

Open this URL in your browser (or use curl):
```
https://search-solaris-poc-vector-store-xxxxx.us-east-1.es.amazonaws.com/_cat/indices?v
```

**Note**: You'll need to authenticate with:
- **Username**: `admin`
- **Password**: `TempP@ssw0rd123!Ch@ngeInProd`

Browser will prompt for basic auth, or use curl:
```bash
curl -u admin:TempP@ssw0rd123!Ch@ngeInProd \
  https://search-solaris-poc-vector-store-xxxxx.us-east-1.es.amazonaws.com/_cat/indices?v
```

## Method 3: AWS CLI

### Check Index via CLI

```bash
# Get the OpenSearch endpoint
OPENSEARCH_ENDPOINT=$(aws opensearch describe-domain \
  --domain-name solaris-poc-vector-store \
  --profile mavenlink-functions \
  --region us-east-1 \
  --query 'DomainStatus.Endpoint' \
  --output text)

# Check if index exists
curl -u admin:TempP@ssw0rd123!Ch@ngeInProd \
  "https://${OPENSEARCH_ENDPOINT}/turbine-documents" | jq
```

**Expected Output if Index Exists**:
```json
{
  "turbine-documents": {
    "aliases": {},
    "mappings": {
      "properties": {
        "text": {"type": "text"},
        "embedding": {
          "type": "knn_vector",
          "dimension": 1536
        },
        ...
      }
    },
    "settings": {...}
  }
}
```

**Expected Output if Index Doesn't Exist**:
```json
{
  "error": {
    "root_cause": [
      {
        "type": "index_not_found_exception",
        "reason": "no such index [turbine-documents]"
      }
    ]
  }
}
```

### List All Indices

```bash
curl -u admin:TempP@ssw0rd123!Ch@ngeInProd \
  "https://${OPENSEARCH_ENDPOINT}/_cat/indices?v"
```

**Expected Output**:
```
health status index              uuid                   pri rep docs.count docs.deleted store.size pri.store.size
green  open   turbine-documents  abc123xyz...           1   0          15            0     45.2kb        45.2kb
```

## Method 4: CloudWatch Logs (Indirect)

Check if the document processor Lambda successfully created the index:

1. Go to [CloudWatch Logs Console](https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups)
2. Find log group: `/aws/lambda/solaris-poc-document-processor`
3. Look for log entries like:
   - `"Creating index turbine-documents"`
   - `"Successfully created index turbine-documents"`
   - `"Index turbine-documents already exists"`

## Quick Check Script

I can create a simple script to check index status. Here's a quick command:

```bash
# Get endpoint and check index
OPENSEARCH_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name VectorStoreStack \
  --profile mavenlink-functions \
  --region us-east-1 \
  --query 'Stacks[0].Outputs[?OutputKey==`OpenSearchEndpoint`].OutputValue' \
  --output text)

echo "Checking index at: ${OPENSEARCH_ENDPOINT}"

curl -u admin:TempP@ssw0rd123!Ch@ngeInProd \
  "https://${OPENSEARCH_ENDPOINT}/turbine-documents/_count" 2>/dev/null | jq
```

**If index exists and has documents**:
```json
{
  "count": 15,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  }
}
```

## Quick Check: Document Processor Lambda Logs

The **fastest way** to check if the index was created is via CloudWatch Logs:

```bash
# Check recent logs for index creation
aws logs tail /aws/lambda/solaris-poc-document-processor \
  --since 1h \
  --profile mavenlink-functions \
  --region us-east-1 \
  --format short \
  | grep -i "index\|stored\|chunk"
```

**Expected output if successful**:
```
Creating index turbine-documents
Successfully created index turbine-documents
Stored 15 chunks in OpenSearch
```

## What to Look For

### ✅ Index Exists with Data
- CloudWatch logs show "Stored X chunks"
- Lambda can query the index successfully
- `docs.count > 0` when accessing via Dashboards

### ⚠️ Index Exists but Empty
- Index exists but `docs.count = 0`
- Check document processor Lambda logs for errors
- Verify PDF processing completed successfully

### ❌ Index Doesn't Exist
- 404 error when querying
- No "Successfully created index" in logs
- Need to trigger document processor Lambda with a PDF

## Troubleshooting

### Can't Access Dashboards
- Check security group allows your IP (if domain is in VPC)
- Verify master username/password
- Check domain is in "Active" state

### Index Not Created
- Check document processor Lambda logs
- Verify Lambda has OpenSearch permissions
- Check OpenSearch endpoint is correct in Lambda environment variables

### Permission Denied
- Verify master username/password
- Check IAM policies if using IAM authentication
- Verify VPC endpoint configuration (if using VPC)
