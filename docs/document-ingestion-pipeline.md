# Document Ingestion Pipeline

**Purpose**: Automated pipeline for processing PDF documents and populating the OpenSearch vector store.

**Status**: ✅ Implemented - Automatic S3-triggered processing

---

## Architecture Overview

The document ingestion pipeline is **separated from user queries** - it runs asynchronously whenever admins upload documents to S3.

```
┌─────────────────────────────────────────────────────────────┐
│              Document Ingestion Pipeline                     │
│                  (Admin-Triggered, Async)                    │
└─────────────────────────────────────────────────────────────┘

Admin uploads PDF to S3
    ↓
S3 Event Notification (automatic)
    ↓
Document Processor Lambda (triggered)
    ↓
┌─────────────────────────────────────┐
│ 1. Load PDF from S3                │
│ 2. Extract text from PDF            │
│ 3. Chunk text (hierarchical)        │
│ 4. Generate embeddings (Bedrock)    │
│ 5. Store in OpenSearch vector store │
└─────────────────────────────────────┘
    ↓
OpenSearch Index Updated
    ↓
Documents available for RAG retrieval


┌─────────────────────────────────────────────────────────────┐
│              Chatbot Query Pipeline                          │
│                  (User-Triggered, Real-time)                 │
└─────────────────────────────────────────────────────────────┘

User asks question
    ↓
Agent Workflow Lambda
    ↓
Retrieve from OpenSearch (RAG)
    ↓
Generate response with LLM
    ↓
Return answer to user
```

---

## How It Works

### Automatic Triggering

**S3 Event Notification**:
- When a PDF is uploaded to `s3://bucket/manuals/*.pdf`
- S3 automatically triggers the Document Processor Lambda
- No manual intervention needed

**Lambda Handler**:
- Receives S3 event notification
- Extracts bucket and key from event
- Extracts metadata (turbine_model, document_type) from S3 key path
- Processes the document automatically

### Metadata Extraction

The handler automatically extracts metadata from the S3 key path:

**Path Pattern**:
```
manuals/{turbine-model}/{document-type}/{filename}.pdf
```

**Examples**:
- `manuals/SMT60-Taurus60/technical-specs/Solaris_SMT60_Technical_Specs.pdf`
  - → `turbine_model: "SMT60"`, `document_type: "technical-specs"`
  
- `manuals/SMT130-Titan130/operational/startup-procedures.pdf`
  - → `turbine_model: "SMT130"`, `document_type: "operational"`
  
- `manuals/TM2500-LM2500/maintenance/scheduled-maintenance.pdf`
  - → `turbine_model: "TM2500"`, `document_type: "maintenance"`

**Supported Turbine Models**:
- `SMT60` / `Taurus60` / `Taurus-60`
- `SMT130` / `Titan130` / `Titan-130`
- `TM2500` / `LM2500`

**Supported Document Types**:
- `technical-specs` / `spec` / `specification`
- `operational` / `operation` / `procedure`
- `maintenance`
- `troubleshooting` / `trouble`
- `reference`
- `safety`
- `manual`

---

## Admin Workflow

### Step 1: Upload Document to S3

Admins upload PDF files to the S3 bucket:

```bash
# Upload via AWS CLI
aws s3 cp Solaris_SMT60_Technical_Specs.pdf \
  s3://solaris-poc-documents-720119760662-us-east-1/manuals/SMT60-Taurus60/technical-specs/ \
  --profile mavenlink-functions

# Or upload via AWS Console
# 1. Go to S3 bucket
# 2. Navigate to manuals/ folder
# 3. Create subfolder structure (e.g., SMT60-Taurus60/technical-specs/)
# 4. Upload PDF file
```

### Step 2: Automatic Processing

**What Happens Automatically**:
1. S3 detects PDF upload
2. S3 sends event notification to Lambda
3. Lambda processes document:
   - Extracts text from PDF
   - Creates chunks with embeddings
   - Stores in OpenSearch
4. Document becomes searchable within minutes

**No Manual Steps Required**:
- ✅ No need to invoke Lambda manually
- ✅ No need to specify metadata (extracted from path)
- ✅ Automatic processing as soon as file is uploaded

### Step 3: Verify Processing

**Check CloudWatch Logs**:
```bash
aws logs tail /aws/lambda/solaris-poc-document-processor \
  --since 10m \
  --profile mavenlink-functions \
  | grep -i "processed\|stored\|chunks"
```

**Check OpenSearch**:
- Query the index to verify documents are stored
- Test RAG retrieval with a query

---

## S3 Bucket Structure

**Recommended Structure**:
```
solaris-poc-documents-{account}-{region}/
└── manuals/
    ├── SMT60-Taurus60/
    │   ├── technical-specs/
    │   │   └── Solaris_SMT60_Technical_Specs.pdf
    │   ├── operational/
    │   │   └── startup-procedures.pdf
    │   ├── maintenance/
    │   │   └── maintenance-schedule.pdf
    │   └── troubleshooting/
    │       └── troubleshooting-guide.pdf
    ├── SMT130-Titan130/
    │   ├── technical-specs/
    │   └── operational/
    └── TM2500-LM2500/
        ├── technical-specs/
        └── operational/
```

**Benefits**:
- Organized by turbine model
- Organized by document type
- Metadata automatically extracted from path
- Easy to find and manage documents

---

## Event Formats

### S3 Event Notification (Automatic)

**Trigger**: PDF uploaded to `manuals/*.pdf`

**Event Format**:
```json
{
  "Records": [
    {
      "eventVersion": "2.1",
      "eventSource": "aws:s3",
      "s3": {
        "bucket": {
          "name": "solaris-poc-documents-720119760662-us-east-1"
        },
        "object": {
          "key": "manuals/SMT60-Taurus60/technical-specs/file.pdf"
        }
      }
    }
  ]
}
```

**Handler Behavior**:
- Extracts bucket and key from event
- Extracts metadata from key path
- Processes document automatically

### Manual Invocation (Testing)

**Trigger**: Manual Lambda invocation

**Event Format**:
```json
{
  "s3_bucket": "solaris-poc-documents-720119760662-us-east-1",
  "s3_key": "manuals/SMT60-Taurus60/technical-specs/file.pdf",
  "turbine_model": "SMT60",  // Optional - extracted from path if not provided
  "document_type": "technical-specs"  // Optional - extracted from path if not provided
}
```

**Handler Behavior**:
- Uses provided metadata if available
- Falls back to extracting from key path if not provided
- Processes document

---

## Processing Steps

### 1. Load PDF from S3

```python
# Download PDF from S3
pdf_bytes = s3_client.get_object(Bucket=bucket, Key=key)['Body'].read()
```

### 2. Extract Text

**Current Implementation**: Mock chunks (for demo)  
**Future Implementation**: Real PDF extraction with `pdfplumber`

```python
# Future: Extract text from PDF
with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
    text = extract_text_from_pdf(pdf)
```

### 3. Chunk Text

**Current Implementation**: 3 mock chunks  
**Future Implementation**: Hierarchical chunking (1000 chars, 200 overlap)

```python
# Future: Chunk text
chunks = chunk_text(text, chunk_size=1000, overlap=200)
```

### 4. Generate Embeddings

```python
# Generate embedding for each chunk
for chunk in chunks:
    embedding = bedrock_runtime.invoke_model(
        modelId="amazon.titan-embed-text-v1",
        body=json.dumps({"inputText": chunk["text"]})
    )
    chunk["embedding"] = embedding
```

### 5. Store in OpenSearch

```python
# Store chunks with embeddings and metadata
for chunk in chunks:
    client.index(
        index="turbine-documents",
        id=f"{source}-{chunk_index}",
        body={
            "text": chunk["text"],
            "embedding": chunk["embedding"],
            "turbine_model": turbine_model,
            "document_type": document_type,
            "source": key,
            "metadata": {...}
        }
    )
```

---

## Benefits of Separated Pipeline

### ✅ Separation of Concerns

- **Document Ingestion**: Admin-triggered, async, batch processing
- **User Queries**: User-triggered, real-time, low latency

### ✅ Scalability

- Document processing can take time (15 min timeout)
- User queries need fast responses (< 5 seconds)
- Separating them prevents user queries from blocking document processing

### ✅ Reliability

- Document processing failures don't affect user queries
- User query failures don't affect document ingestion
- Independent retry logic and error handling

### ✅ Operational Efficiency

- Admins just upload files - no manual Lambda invocations
- Automatic metadata extraction from file paths
- No need to coordinate between ingestion and query systems

### ✅ Cost Optimization

- Document processing runs only when needed (file uploads)
- User queries run on-demand
- No idle processing waiting for documents

---

## Monitoring

### CloudWatch Metrics

**Document Processor Lambda**:
- Invocations (should match PDF uploads)
- Duration (processing time per document)
- Errors (failed processing)
- Throttles (if too many uploads at once)

### CloudWatch Logs

**Key Log Messages**:
- `"Processing S3 event: s3://..."`
- `"Extracted metadata: turbine_model=..., document_type=..."`
- `"Stored X chunks in OpenSearch"`
- `"Error: ..."` (if processing fails)

### Alarms

**Recommended Alarms**:
- High error rate (> 10% errors)
- Long processing time (> 10 minutes)
- Throttled invocations

---

## Future Enhancements

### 1. Real PDF Processing

**Current**: Mock chunks  
**Future**: Real PDF text extraction with `pdfplumber`

### 2. Metadata File Support

**Option**: Support metadata JSON files alongside PDFs:
```
manuals/SMT60/file.pdf
manuals/SMT60/file.pdf.metadata.json  // Optional metadata override
```

### 3. Processing Status Tracking

**Option**: Store processing status in DynamoDB:
- Document ID (S3 key)
- Processing status (pending, processing, completed, failed)
- Processing timestamp
- Chunks created
- Error messages (if any)

### 4. Batch Processing

**Option**: Process multiple documents in parallel for large uploads

### 5. Reprocessing Support

**Option**: Allow admins to trigger reprocessing of existing documents:
- Via S3 event (re-upload file)
- Via manual Lambda invocation
- Via API endpoint

---

## Testing

### Test Automatic Processing

1. **Upload a PDF**:
   ```bash
   aws s3 cp test.pdf \
     s3://solaris-poc-documents-720119760662-us-east-1/manuals/SMT60-Taurus60/technical-specs/ \
     --profile mavenlink-functions
   ```

2. **Check Lambda Invocation**:
   ```bash
   aws logs tail /aws/lambda/solaris-poc-document-processor \
     --since 2m \
     --profile mavenlink-functions \
     --follow
   ```

3. **Verify Processing**:
   - Check logs for "Stored X chunks"
   - Query OpenSearch to verify documents are searchable

### Test Manual Invocation

```bash
aws lambda invoke \
  --function-name solaris-poc-document-processor \
  --payload '{
    "s3_bucket": "solaris-poc-documents-720119760662-us-east-1",
    "s3_key": "manuals/SMT60-Taurus60/technical-specs/test.pdf"
  }' \
  --cli-binary-format raw-in-base64-out \
  --profile mavenlink-functions \
  /tmp/test-output.json
```

---

## Summary

✅ **Automatic Processing**: PDF uploads trigger Lambda automatically  
✅ **Metadata Extraction**: Turbine model and document type extracted from path  
✅ **Separated Pipeline**: Document ingestion independent from user queries  
✅ **Admin-Friendly**: Just upload files, everything else is automatic  
✅ **Scalable**: Async processing doesn't block user queries  
✅ **Reliable**: Independent error handling and retry logic

**Next Steps**:
1. Configure OpenSearch IAM authentication (fix 403 errors)
2. Test automatic processing by uploading a PDF
3. Implement real PDF text extraction (replace mock chunks)
4. Add processing status tracking (optional)

