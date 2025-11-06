# Analytics Pipeline Architecture Design

**Purpose**: Detailed infrastructure architecture for the analytics and learning pipeline

**Date**: 2025-11-05  
**Status**: Architecture Design  
**Related**: `analytics-pipeline-learning.md`

---

## Architecture Overview

### High-Level Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    Real-Time Session Flow                        │
│  User → API Gateway → AgentCore → Response                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ↓ (Async Event)
┌─────────────────────────────────────────────────────────────────┐
│              Analytics & Learning Pipeline                       │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  1. Event Collection Layer                               │  │
│  │     - EventBridge Rules                                  │  │
│  │     - Session Logger Lambda                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             ↓                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  2. Data Storage Layer                                   │  │
│  │     - S3 Data Lake (raw/processed)                       │  │
│  │     - DynamoDB (patterns, user profiles)                 │  │
│  │     - OpenSearch (pattern search)                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             ↓                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  3. Processing Layer                                     │  │
│  │     - Intent Extraction Lambda                           │  │
│  │     - Pattern Recognition Lambda                         │  │
│  │     - Flow Analysis Lambda                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             ↓                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  4. Training Layer                                       │  │
│  │     - SageMaker Training Jobs                            │  │
│  │     - Model Registry                                     │  │
│  │     - Model Deployment                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             ↓                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  5. Prediction Layer                                     │  │
│  │     - Predictive Guidance Lambda                         │  │
│  │     - Pattern Matcher Service                            │  │
│  │     - QueryTransformer Integration                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component 1: Event Collection Layer

### EventBridge Rule

**Purpose**: Trigger analytics pipeline on session events

**Configuration**:
```json
{
  "Name": "SessionAnalyticsRule",
  "EventPattern": {
    "source": ["solaris-poc.agentcore"],
    "detail-type": ["Session Completed", "Query Processed"],
    "detail": {
      "action": ["query", "response"]
    }
  },
  "Targets": [
    {
      "Arn": "arn:aws:lambda:us-east-1:ACCOUNT:function:SessionLogger",
      "Id": "SessionLoggerTarget"
    }
  ]
}
```

**Event Schema**:
```json
{
  "source": "solaris-poc.agentcore",
  "detail-type": "Query Processed",
  "detail": {
    "session_id": "session-123",
    "query": "How do I troubleshoot low oil pressure?",
    "response": {...},
    "metadata": {
      "timestamp": "2025-11-05T10:30:00Z",
      "duration_ms": 2500,
      "confidence_score": 0.85
    }
  }
}
```

### Session Logger Lambda

**Function**: `SessionLogger`

**Purpose**: Capture and structure session data for analytics

**Code Structure**:
```python
def lambda_handler(event, context):
    """
    Process session events and store in analytics data lake.
    """
    # Extract event data
    session_data = extract_session_data(event)
    
    # Enrich with metadata
    enriched_data = enrich_with_metadata(session_data)
    
    # Extract intent (optional, can be done later)
    intent = extract_intent_quick(session_data['query'])
    
    # Structure for storage
    analytics_record = {
        "session_id": session_data['session_id'],
        "timestamp": session_data['timestamp'],
        "query": session_data['query'],
        "intent": intent,
        "response": session_data['response'],
        "metadata": enriched_data,
        "partition_date": get_partition_date(session_data['timestamp'])
    }
    
    # Store in S3
    s3_key = f"raw/sessions/{analytics_record['partition_date']}/sessions-{timestamp}.json"
    s3_client.put_object(
        Bucket=ANALYTICS_BUCKET,
        Key=s3_key,
        Body=json.dumps(analytics_record),
        ContentType="application/json"
    )
    
    return {"statusCode": 200}
```

**Configuration**:
- **Runtime**: Python 3.12
- **Memory**: 256 MB
- **Timeout**: 30 seconds
- **Concurrency**: 100 (auto-scales)
- **IAM Permissions**:
  - `s3:PutObject` on analytics bucket
  - `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`

---

## Component 2: Data Storage Layer

### S3 Data Lake Structure

**Bucket**: `solaris-poc-analytics-{account}-{region}`

**Structure**:
```
solaris-poc-analytics-{account}-{region}/
├── raw/
│   ├── sessions/
│   │   ├── year=2025/
│   │   │   ├── month=11/
│   │   │   │   ├── day=05/
│   │   │   │   │   ├── sessions-2025-11-05-00-00.json
│   │   │   │   │   ├── sessions-2025-11-05-01-00.json
│   │   │   │   │   └── ...
│   │   │   │   └── ...
│   │   │   └── ...
│   │   └── ...
│   └── events/
│       └── ...
├── processed/
│   ├── intents/
│   │   ├── year=2025/month=11/day=05/
│   │   │   └── intents-2025-11-05.json
│   │   └── ...
│   ├── patterns/
│   │   ├── flows/
│   │   │   └── flow-patterns-{date}.json
│   │   └── sequences/
│   │       └── sequence-patterns-{date}.json
│   └── training-data/
│       ├── intent-classifier/
│       │   └── training-data-{version}.jsonl
│       └── pattern-recognition/
│           └── training-data-{version}.jsonl
└── models/
    ├── intent-classifier/
    │   ├── v1/
    │   │   └── model.tar.gz
    │   └── v2/
    │       └── model.tar.gz
    └── pattern-matcher/
        └── ...
```

**Lifecycle Policies**:
```python
# Raw data: 90 days in Standard, then Glacier
lifecycle_configuration = {
    "Rules": [
        {
            "Id": "RawDataLifecycle",
            "Status": "Enabled",
            "Prefix": "raw/",
            "Transitions": [
                {
                    "Days": 90,
                    "StorageClass": "GLACIER"
                }
            ]
        },
        # Processed data: 1 year in Standard, then Glacier
        {
            "Id": "ProcessedDataLifecycle",
            "Status": "Enabled",
            "Prefix": "processed/",
            "Transitions": [
                {
                    "Days": 365,
                    "StorageClass": "GLACIER"
                }
            ]
        }
    ]
}
```

**Encryption**: SSE-S3 (AWS managed keys)

### DynamoDB Tables

#### Pattern Database Table

**Table**: `solaris-poc-patterns`

**Schema**:
```python
{
    "TableName": "solaris-poc-patterns",
    "KeySchema": [
        {"AttributeName": "pattern_id", "KeyType": "HASH"},
        {"AttributeName": "pattern_type", "KeyType": "RANGE"}
    ],
    "AttributeDefinitions": [
        {"AttributeName": "pattern_id", "AttributeType": "S"},
        {"AttributeName": "pattern_type", "AttributeType": "S"},
        {"AttributeName": "frequency", "AttributeType": "N"}
    ],
    "GlobalSecondaryIndexes": [
        {
            "IndexName": "frequency-index",
            "KeySchema": [
                {"AttributeName": "pattern_type", "KeyType": "HASH"},
                {"AttributeName": "frequency", "KeyType": "RANGE"}
            ],
            "Projection": {"ProjectionType": "ALL"}
        }
    ],
    "BillingMode": "PAY_PER_REQUEST"
}
```

**Items**:
```json
{
  "pattern_id": "flow-oil-pressure-troubleshooting",
  "pattern_type": "flow",
  "sequence": [
    {"intent": "troubleshooting", "topic": "oil_pressure"},
    {"intent": "procedure", "topic": "check_filters"},
    {"intent": "procedure", "topic": "replace_parts"}
  ],
  "frequency": 45,
  "success_rate": 0.92,
  "avg_completion_time": 180,
  "last_updated": "2025-11-05T10:00:00Z"
}
```

#### User Profile Table

**Table**: `solaris-poc-user-profiles`

**Schema**:
```python
{
    "TableName": "solaris-poc-user-profiles",
    "KeySchema": [
        {"AttributeName": "user_id", "KeyType": "HASH"}
    ],
    "AttributeDefinitions": [
        {"AttributeName": "user_id", "AttributeType": "S"}
    ],
    "BillingMode": "PAY_PER_REQUEST"
}
```

**Items**:
```json
{
  "user_id": "operator-456",
  "preferred_turbine_models": ["SMT60", "SMT130"],
  "common_intents": ["troubleshooting", "procedure"],
  "question_style": "technical",
  "session_count": 45,
  "avg_session_length": 5,
  "last_active": "2025-11-05T10:30:00Z",
  "learned_preferences": {
    "detail_level": "high",
    "preferred_flow": "direct_troubleshooting"
  }
}
```

### OpenSearch Index (Optional)

**Index**: `session-patterns`

**Purpose**: Fast pattern matching and similarity search

**Mapping**:
```json
{
  "mappings": {
    "properties": {
      "pattern_sequence": {
        "type": "text",
        "analyzer": "standard"
      },
      "pattern_embedding": {
        "type": "knn_vector",
        "dimension": 1536
      },
      "pattern_metadata": {
        "type": "object"
      }
    }
  }
}
```

---

## Component 3: Processing Layer

### Intent Extraction Lambda

**Function**: `IntentExtractor`

**Purpose**: Extract and classify intents from session data

**Trigger**: EventBridge scheduled rule (daily at 2 AM)

**Code Structure**:
```python
def lambda_handler(event, context):
    """
    Process yesterday's session data and extract intents.
    """
    # Get yesterday's date
    yesterday = get_yesterday_date()
    
    # Load session data from S3
    sessions = load_sessions_from_s3(yesterday)
    
    # Extract intents using LLM
    intent_data = []
    for session in sessions:
        for turn in session['conversation']:
            intent = classify_intent_with_llm(turn['query'])
            intent_data.append({
                "query": turn['query'],
                "intent": intent['primary'],
                "sub_intent": intent.get('sub'),
                "confidence": intent['confidence'],
                "metadata": turn['metadata']
            })
    
    # Store processed intents
    save_intents_to_s3(intent_data, yesterday)
    
    # Trigger pattern recognition if enough data
    if len(intent_data) > 100:
        trigger_pattern_recognition()
    
    return {"statusCode": 200, "processed": len(intent_data)}
```

**LLM Intent Classification**:
```python
def classify_intent_with_llm(query):
    """
    Use Bedrock LLM to classify intent with few-shot learning.
    """
    prompt = f"""
    Classify the intent of this operator query about gas turbines.
    
    Query: {query}
    
    Intent categories:
    - troubleshooting: Problem diagnosis and resolution
    - procedure: Step-by-step instructions
    - status_check: Current state queries
    - maintenance: Maintenance scheduling/inquiries
    - safety: Safety-related questions
    - documentation: Manual/documentation requests
    
    Examples:
    Query: "How do I fix low oil pressure?"
    Intent: {{"primary": "troubleshooting", "sub": "oil_system", "confidence": 0.95}}
    
    Query: "What's the startup procedure for SMT60?"
    Intent: {{"primary": "procedure", "sub": "startup", "confidence": 0.92}}
    
    Return JSON with primary intent, optional sub_intent, and confidence score.
    """
    
    response = bedrock.invoke_model(
        modelId="amazon.nova-pro-v1:0",
        body=json.dumps({"inputText": prompt})
    )
    
    return json.loads(response['body'].read())
```

### Pattern Recognition Lambda

**Function**: `PatternRecognizer`

**Purpose**: Identify common question flows and patterns

**Trigger**: EventBridge rule (after intent extraction completes)

**Code Structure**:
```python
def lambda_handler(event, context):
    """
    Analyze intent data to identify patterns.
    """
    # Load processed intents
    intents = load_intents_from_s3(event['date'])
    
    # Analyze flows
    flows = analyze_flows(intents)
    
    # Analyze sequences
    sequences = analyze_sequences(intents)
    
    # Analyze user behavior
    user_patterns = analyze_user_behavior(intents)
    
    # Store patterns
    save_patterns_to_dynamodb(flows, sequences)
    save_patterns_to_s3(flows, sequences, user_patterns)
    
    # Update pattern database
    update_pattern_database(flows, sequences)
    
    return {"statusCode": 200, "patterns_found": len(flows)}
```

**Flow Analysis**:
```python
def analyze_flows(intents):
    """
    Identify common question flow patterns.
    """
    # Group by session
    sessions = group_by_session(intents)
    
    # Extract flows
    flows = []
    for session_id, session_intents in sessions.items():
        flow = [intent['intent'] for intent in session_intents]
        flows.append(flow)
    
    # Find common patterns
    pattern_counts = Counter([tuple(flow) for flow in flows])
    
    # Extract top patterns
    top_patterns = pattern_counts.most_common(50)
    
    return [
        {
            "pattern_id": f"flow-{hash(flow)}",
            "sequence": list(flow),
            "frequency": count,
            "sessions": count
        }
        for flow, count in top_patterns
    ]
```

### Flow Analysis Lambda

**Function**: `FlowAnalyzer`

**Purpose**: Deep analysis of conversation flows and optimization

**Trigger**: Weekly scheduled job

**Analysis Types**:
- Flow efficiency (shortest paths to resolution)
- Common dead-ends
- Optimal troubleshooting paths
- User journey optimization

---

## Component 4: Training Layer

### SageMaker Training Pipeline

**Purpose**: Train intent classifiers and pattern models

**Components**:

#### Training Job Configuration

**Intent Classifier Training**:
```python
training_job_config = {
    "TrainingJobName": f"intent-classifier-{timestamp}",
    "AlgorithmSpecification": {
        "TrainingImage": "your-custom-image",
        "TrainingInputMode": "File"
    },
    "RoleArn": "arn:aws:iam::ACCOUNT:role/SageMakerTrainingRole",
    "InputDataConfig": [
        {
            "ChannelName": "training",
            "DataSource": {
                "S3DataSource": {
                    "S3Uri": "s3://analytics-bucket/processed/training-data/intent-classifier/",
                    "S3DataType": "S3Prefix"
                }
            }
        }
    ],
    "OutputDataConfig": {
        "S3OutputPath": "s3://analytics-bucket/models/intent-classifier/"
    },
    "ResourceConfig": {
        "InstanceType": "ml.m5.xlarge",
        "InstanceCount": 1,
        "VolumeSizeInGB": 30
    },
    "StoppingCondition": {
        "MaxRuntimeInSeconds": 3600
    },
    "HyperParameters": {
        "learning_rate": "0.001",
        "epochs": "10",
        "batch_size": "32"
    }
}
```

**Model Training Options**:

1. **Fine-tune Bedrock Model** (Recommended for POC)
   - Use Bedrock fine-tuning API
   - Base model: Claude Haiku or Nova Pro
   - Task: Intent classification

2. **Train Custom Model** (For production)
   - Use SageMaker built-in algorithms
   - Or custom container with PyTorch/TensorFlow
   - Deploy as SageMaker endpoint

#### Model Registry

**SageMaker Model Registry**:
- Version control for models
- A/B testing capabilities
- Model approval workflow
- Automatic rollback

#### Model Deployment

**SageMaker Endpoint** (for custom models):
```python
endpoint_config = {
    "EndpointConfigName": "intent-classifier-endpoint",
    "ProductionVariants": [
        {
            "VariantName": "AllTraffic",
            "ModelName": "intent-classifier-v2",
            "InitialInstanceCount": 1,
            "InstanceType": "ml.t2.medium",
            "InitialVariantWeight": 1.0
        }
    ]
}
```

**Lambda Integration** (for Bedrock models):
- Use Bedrock API directly (no endpoint needed)
- Models are managed by AWS

---

## Component 5: Prediction Layer

### Predictive Guidance Lambda

**Function**: `PredictiveGuidance`

**Purpose**: Provide proactive suggestions based on learned patterns

**Integration**: Called by QueryTransformer node

**Code Structure**:
```python
def get_predictive_guidance(session_id, current_flow, user_id=None):
    """
    Generate predictive guidance based on learned patterns.
    """
    # Load current flow
    flow_so_far = current_flow
    
    # Match against learned patterns
    matching_patterns = find_matching_patterns(flow_so_far)
    
    # Get user-specific patterns if available
    if user_id:
        user_patterns = get_user_patterns(user_id)
        matching_patterns = combine_patterns(matching_patterns, user_patterns)
    
    # Generate suggestions
    suggestions = []
    for pattern in matching_patterns:
        next_steps = pattern.get('next_likely_intents', [])
        suggestions.extend([
            {
                "suggestion": f"Users typically ask: {step['intent']}",
                "confidence": step['probability'],
                "pattern_id": pattern['pattern_id']
            }
            for step in next_steps
        ])
    
    # Return top suggestions
    return sorted(suggestions, key=lambda x: x['confidence'], reverse=True)[:3]
```

### Pattern Matcher Service

**Purpose**: Fast pattern matching against learned flows

**Implementation Options**:

1. **DynamoDB Query** (Simple)
   - Query pattern database
   - Match current flow against stored patterns
   - Fast but limited matching capabilities

2. **OpenSearch** (Recommended)
   - Vector similarity search
   - Semantic matching of flows
   - More flexible pattern matching

**OpenSearch Query**:
```python
def find_matching_patterns(current_flow):
    """
    Find patterns similar to current flow using OpenSearch.
    """
    # Generate embedding for current flow
    flow_embedding = generate_embedding(current_flow)
    
    # Search OpenSearch
    query = {
        "size": 10,
        "query": {
            "knn": {
                "pattern_embedding": {
                    "vector": flow_embedding,
                    "k": 10
                }
            }
        }
    }
    
    response = opensearch_client.search(
        index="session-patterns",
        body=query
    )
    
    return response['hits']['hits']
```

### QueryTransformer Integration

**Enhanced QueryTransformer with Predictive Guidance**:
```python
def query_transformer_node(state: AgentState) -> AgentState:
    """
    Enhanced transformer with predictive guidance.
    """
    # Original intent detection
    intent = detect_intent(state.query)
    turbine_model = detect_turbine_model(state.query)
    
    # Get predictive guidance
    current_flow = [msg['intent'] for msg in state.conversation_history]
    suggestions = get_predictive_guidance(
        session_id=state.session_id,
        current_flow=current_flow,
        user_id=state.user_id
    )
    
    # Enhance query with suggestions context
    enhanced_query = state.query
    if suggestions:
        suggestions_text = "\n".join([
            f"- {s['suggestion']}" for s in suggestions
        ])
        enhanced_query = f"{state.query}\n\n[Context: Users typically ask: {suggestions_text}]"
    
    state.transformed_query = enhanced_query
    state.intent = intent
    state.turbine_model = turbine_model
    state.predicted_suggestions = suggestions
    
    return state
```

---

## Infrastructure as Code (CDK)

### Analytics Stack Structure

```python
class AnalyticsStack(cdk.Stack):
    """Analytics and learning pipeline infrastructure."""
    
    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        # S3 Data Lake
        self.analytics_bucket = self._create_data_lake()
        
        # EventBridge Rules
        self.session_rule = self._create_eventbridge_rules()
        
        # Lambda Functions
        self.session_logger = self._create_session_logger()
        self.intent_extractor = self._create_intent_extractor()
        self.pattern_recognizer = self._create_pattern_recognizer()
        self.predictive_guidance = self._create_predictive_guidance()
        
        # DynamoDB Tables
        self.patterns_table = self._create_patterns_table()
        self.user_profiles_table = self._create_user_profiles_table()
        
        # SageMaker (if needed)
        # self.training_pipeline = self._create_training_pipeline()
        
        # OpenSearch (optional)
        # self.pattern_index = self._create_opensearch_index()
```

### Key Resources

**S3 Bucket**:
```python
analytics_bucket = s3.Bucket(
    self,
    "AnalyticsDataLake",
    bucket_name=f"solaris-poc-analytics-{account}-{region}",
    encryption=s3.BucketEncryption.S3_MANAGED,
    versioned=True,
    lifecycle_rules=[lifecycle_configuration]
)
```

**EventBridge Rule**:
```python
session_rule = events.Rule(
    self,
    "SessionAnalyticsRule",
    description="Trigger analytics on session events",
    event_pattern=events.EventPattern(
        source=["solaris-poc.agentcore"],
        detail_type=["Session Completed"]
    )
)
session_rule.add_target(targets.LambdaFunction(session_logger))
```

**Lambda Functions** (similar structure for all):
```python
session_logger = _lambda.Function(
    self,
    "SessionLogger",
    runtime=_lambda.Runtime.PYTHON_3_12,
    handler="handler.lambda_handler",
    code=_lambda.Code.from_asset("lambda/analytics/session-logger"),
    environment={
        "ANALYTICS_BUCKET": analytics_bucket.bucket_name
    },
    timeout=Duration.seconds(30)
)
analytics_bucket.grant_write(session_logger)
```

---

## Cost Estimation

### Monthly Costs (Estimated)

| Component | Resource | Estimated Cost |
|-----------|----------|----------------|
| **Storage** | S3 (100 GB) | ~$2.30 |
| **Storage** | S3 Glacier (500 GB) | ~$1.00 |
| **Compute** | Lambda (100K invocations) | ~$0.20 |
| **Database** | DynamoDB (on-demand) | ~$1.25 |
| **Training** | SageMaker (monthly job) | ~$5.00 |
| **Total** | | **~$9.75/month** |

**Note**: Costs scale with usage. For POC, should be minimal.

---

## Security & Compliance

### IAM Roles

**Session Logger Role**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl"
      ],
      "Resource": "arn:aws:s3:::solaris-poc-analytics-*/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

### Data Privacy

- **Anonymization**: Remove PII before storage
- **Encryption**: All data encrypted at rest (S3, DynamoDB)
- **Access Control**: Separate IAM roles for analytics pipeline
- **Retention**: Follow data retention policies (90 days raw, 1 year processed)

---

## Monitoring & Observability

### CloudWatch Metrics

**Custom Metrics**:
- Sessions logged per hour
- Intent extraction accuracy
- Pattern recognition success rate
- Training job success/failure
- Predictive guidance hit rate

### CloudWatch Dashboards

**Analytics Dashboard**:
- Session volume trends
- Intent distribution
- Pattern frequency
- Model performance metrics
- Cost tracking

### Alarms

- Failed session logging
- Training job failures
- S3 storage threshold
- DynamoDB throttling

---

## Next Steps

1. **Implement CDK Stack**: Create `AnalyticsStack` in infrastructure
2. **Build Lambda Functions**: Implement session logger and processors
3. **Set up S3 Data Lake**: Create bucket with proper structure
4. **Create DynamoDB Tables**: Pattern and user profile tables
5. **Implement Intent Extraction**: Initial version with LLM classification
6. **Build Pattern Recognition**: Basic flow analysis
7. **Test End-to-End**: Validate pipeline with sample data
8. **Integrate with AgentCore**: Connect predictive guidance to QueryTransformer

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-05  
**Status**: Architecture Complete - Ready for Implementation


