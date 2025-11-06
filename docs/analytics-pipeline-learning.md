# Analytics Pipeline for Learning from User Sessions

**Purpose**: Design document for learning from user sessions to improve intent classification, anticipate user needs, and provide predictive guidance.

**Date**: 2025-11-05  
**Status**: Design Phase

---

## Executive Summary

This document outlines an analytics pipeline that learns from user sessions to:
- Train intent classifiers on real user questions
- Identify common question patterns and flows
- Provide predictive guidance based on learned patterns
- Continuously improve the operator assistant's effectiveness

**Key Insight**: While AgentCore provides real-time session memory, we need a separate analytics pipeline to extract, analyze, and learn from session data for long-term improvement.

---

## Problem Statement

### Client Requirements

The client wants to:
1. **Learn from user sessions**: Understand the types of questions operators ask
2. **Identify patterns**: Recognize typical question flows and troubleshooting paths
3. **Anticipate needs**: Predict what operators will ask next based on patterns
4. **Guide proactively**: Suggest next steps based on learned patterns
5. **Train on intents**: Use real conversations to improve intent classification

### Current State

- **AgentCore Memory**: Handles real-time session memory (conversation context)
- **DynamoDB**: Stores session metadata (currently manual, would be replaced by AgentCore)
- **No Learning Pipeline**: No mechanism to extract patterns or train on session data

### Gap

AgentCore memory is optimized for **operational use** (real-time context), not **analytical use** (learning from patterns). We need a separate pipeline to:
- Extract structured data from sessions
- Analyze patterns and flows
- Train intent classifiers
- Build predictive models

---

## Architecture Overview

### Current Session Flow

```
User Query 
    ↓
AgentCore (Real-time Memory)
    ↓
Response
```

### With Analytics Pipeline

```
User Query 
    ↓
AgentCore (Real-time Memory) → Response
    ↓ (Async logging)
EventBridge Trigger
    ↓
Session Analytics Lambda
    ↓
S3 Data Lake (Analytics Storage)
    ↓
Intent Extraction Service
    ↓
Pattern Recognition Service
    ↓
Training Pipeline → Intent Classifier Model
    ↓
Predictive Guidance Service → Improved Responses
```

---

## Key Architectural Components

### 1. Session Logger (EventBridge + Lambda)

**Purpose**: Capture all session interactions for analysis

**Trigger**: After each AgentCore invocation completes

**Data Captured**:
```json
{
  "session_id": "session-123",
  "query": "How do I troubleshoot low oil pressure?",
  "intent": "troubleshooting",
  "turbine_model": "SMT60",
  "context": {
    "previous_queries": ["question1", "question2"],
    "flow_position": 3,
    "user_id": "operator-456"
  },
  "response": {
    "content": "...",
    "confidence_score": 0.85,
    "citations": [...]
  },
  "metadata": {
    "timestamp": "2025-11-05T10:30:00Z",
    "session_duration": 120,
    "user_feedback": "helpful"
  }
}
```

**Storage**: S3 Data Lake (raw logs)

### 2. Analytics Storage (S3 Data Lake)

**Purpose**: Long-term storage of structured session data

**Structure**:
```
s3://solaris-poc-analytics/
├── raw/
│   ├── sessions/
│   │   ├── 2025/11/05/sessions-2025-11-05.json
│   │   └── ...
│   └── events/
│       └── ...
├── processed/
│   ├── intents/
│   │   ├── training-data-2025-11-05.json
│   │   └── ...
│   └── patterns/
│       └── flow-patterns-2025-11-05.json
└── models/
    └── intent-classifier-v2/
```

**Data Formats**:
- **Raw Sessions**: Complete conversation logs
- **Processed Intents**: Extracted intent classifications
- **Pattern Data**: Identified flow patterns
- **Training Data**: Curated datasets for model training

### 3. Intent Extraction Service

**Purpose**: Extract and classify intents from conversations

**Process**:
1. Load session logs from S3
2. Extract queries and context
3. Use LLM to classify intents (few-shot learning)
4. Build training dataset
5. Store structured intent data

**Intent Categories**:
- `troubleshooting` - Problem diagnosis and resolution
- `procedure` - Step-by-step instructions
- `status_check` - Current state queries
- `maintenance` - Maintenance scheduling/inquiries
- `safety` - Safety-related questions
- `documentation` - Manual/documentation requests

**Training Data Format**:
```json
{
  "query": "How do I troubleshoot low oil pressure on SMT60?",
  "intent": "troubleshooting",
  "sub_intent": "oil_system",
  "turbine_model": "SMT60",
  "context": "previous_queries: [...]",
  "flow_position": 2,
  "confidence": 0.92
}
```

### 4. Pattern Recognition Service

**Purpose**: Identify common question flows and user behavior patterns

**Patterns Analyzed**:

#### Question Flow Patterns
- **Sequence Analysis**: Common question sequences
  - Example: "oil pressure" → "check filters" → "replace parts"
- **Follow-up Patterns**: Typical next questions
  - Example: After troubleshooting, users often ask about prevention
- **Session Depth**: How many questions before resolution
  - Example: Average 3-5 questions for troubleshooting

#### User Behavior Patterns
- **Time-based Patterns**: Peak usage times, common issues by time
- **Turbine-specific Patterns**: Different patterns per turbine model
- **Operator Patterns**: Individual operator preferences/styles

**Output**: Flow graphs, pattern databases, predictive models

### 5. Training Pipeline

**Purpose**: Train/fine-tune intent classifiers and pattern models

**Components**:

#### Intent Classifier Training
```python
# Option A: Fine-tune Bedrock Model
fine_tune_bedrock_model(
    base_model="anthropic.claude-3-haiku-20240307-v1:0",
    training_data=intent_training_data,
    task="intent_classification"
)

# Option B: Train Classification Model
train_bert_classifier(
    model="bert-base-uncased",
    training_data=intent_training_data,
    num_intents=10
)

# Option C: Few-shot Learning with Prompts
# Use existing LLM with few-shot examples
```

#### Pattern Model Training
- Build flow prediction models
- Train sequence-to-sequence models for next-question prediction
- Create user behavior models for personalization

**Schedule**: Periodic training (weekly/monthly) as new data accumulates

### 6. Predictive Guidance Service

**Purpose**: Use learned patterns to improve real-time responses

**Features**:

#### Proactive Suggestions
- Predict next likely questions based on current flow
- Suggest related topics operator might need
- Anticipate troubleshooting steps

#### Personalized Guidance
- Adapt to operator's typical question style
- Learn from operator's previous sessions
- Provide personalized recommendations

#### Flow Optimization
- Guide operators toward efficient troubleshooting paths
- Prevent common dead-ends
- Suggest shortcuts based on learned patterns

**Integration**: Updates QueryTransformer node with learned patterns

---

## Data Flow

### Real-Time Flow (No Impact on Performance)

```
1. User submits query
   ↓
2. AgentCore processes (with memory)
   ↓
3. Response returned to user
   ↓
4. EventBridge triggers async (non-blocking)
   ↓
5. Session Logger Lambda captures data
   ↓
6. Data stored in S3 (async)
```

### Batch Processing Flow

```
1. Scheduled job (EventBridge daily trigger)
   ↓
2. Intent Extraction Service processes last 24 hours
   ↓
3. Pattern Recognition Service analyzes flows
   ↓
4. Training data prepared
   ↓
5. Models trained (if sufficient new data)
   ↓
6. Models deployed to Predictive Guidance Service
```

### Prediction Flow

```
1. User submits query
   ↓
2. QueryTransformer extracts intent (using trained classifier)
   ↓
3. Pattern Matcher checks current flow against learned patterns
   ↓
4. Predictive Guidance suggests next steps
   ↓
5. Response enhanced with proactive suggestions
```

---

## Storage Strategy

### Multi-Layer Storage Approach

| Layer | Storage | Purpose | Retention |
|-------|---------|---------|-----------|
| **Real-time Memory** | AgentCore | Session context | Session duration |
| **Raw Analytics** | S3 Data Lake | Complete session logs | 90 days |
| **Processed Data** | S3 | Structured intent/pattern data | 1 year |
| **Training Data** | S3 | Curated datasets | Permanent |
| **Pattern Database** | DynamoDB/OpenSearch | Fast pattern lookup | Permanent |
| **User Profiles** | DynamoDB | Personalized preferences | Permanent |
| **Model Artifacts** | S3 | Trained models | Permanent |

### Why Separate Storage?

**AgentCore Memory**:
- Optimized for real-time access
- Managed by AWS (not directly queryable)
- Session-scoped (not designed for analytics)

**Analytics Storage**:
- Optimized for batch analysis
- Directly queryable (S3, Athena, etc.)
- Long-term retention for learning
- Structured for training pipelines

---

## Benefits

### 1. Continuous Improvement

**Intent Classification**:
- Starts with rule-based/intent detection
- Improves over time with real user data
- Adapts to actual operator language patterns

**Pattern Recognition**:
- Identifies common troubleshooting paths
- Learns efficient resolution flows
- Discovers edge cases and exceptions

### 2. Predictive Guidance

**Proactive Suggestions**:
- "Based on similar issues, you might also want to check..."
- "Operators typically follow this troubleshooting path..."
- "After resolving this, users often ask about..."

**Personalization**:
- Adapts to individual operator styles
- Learns from operator's history
- Provides tailored recommendations

### 3. Better User Experience

**Anticipation**:
- Suggests next questions before operator asks
- Guides toward resolution faster
- Reduces back-and-forth

**Efficiency**:
- Shortcuts to common solutions
- Prevention of common dead-ends
- Streamlined troubleshooting paths

### 4. Business Intelligence

**Analytics**:
- Understand operator needs
- Identify knowledge gaps
- Track common issues
- Measure assistant effectiveness

---

## Implementation Phases

### Phase 1: Foundation (Current)

- ✅ AgentCore memory for real-time sessions
- ✅ Basic session logging
- ⏳ Analytics storage setup

### Phase 2: Data Collection

- [ ] EventBridge triggers for session logging
- [ ] Session Analytics Lambda
- [ ] S3 Data Lake structure
- [ ] Basic intent extraction

### Phase 3: Pattern Recognition

- [ ] Intent extraction service
- [ ] Flow pattern analysis
- [ ] Pattern database (DynamoDB/OpenSearch)

### Phase 4: Training Pipeline

- [ ] Training data preparation
- [ ] Intent classifier training
- [ ] Pattern model training
- [ ] Model deployment pipeline

### Phase 5: Predictive Guidance

- [ ] Predictive Guidance Service
- [ ] Integration with QueryTransformer
- [ ] Proactive suggestions
- [ ] Personalization features

---

## Technical Considerations

### Performance

- **Async Processing**: Analytics pipeline doesn't impact real-time response times
- **Batch Processing**: Pattern recognition runs on schedule, not real-time
- **Caching**: Pattern database cached for fast lookup

### Privacy & Security

- **Data Anonymization**: Remove PII from analytics data
- **Access Control**: Separate IAM roles for analytics pipeline
- **Encryption**: Encrypt data at rest and in transit
- **Compliance**: Follow data retention policies

### Scalability

- **S3**: Unlimited storage for analytics data
- **Lambda**: Auto-scales for batch processing
- **DynamoDB**: On-demand capacity for pattern database
- **SageMaker**: Managed training infrastructure

### Cost Optimization

- **S3 Lifecycle Policies**: Move old data to Glacier
- **Scheduled Processing**: Batch jobs run during off-peak hours
- **Selective Training**: Only train when sufficient new data
- **Model Caching**: Cache models to reduce inference costs

---

## Next Steps

1. **Design Analytics Pipeline Architecture** (detailed infrastructure)
2. **Implement Session Logger** (EventBridge + Lambda)
3. **Set up S3 Data Lake** (structure and lifecycle policies)
4. **Build Intent Extraction Service** (initial version)
5. **Create Pattern Recognition Service** (basic flow analysis)
6. **Develop Training Pipeline** (automated model training)

---

## References

- AWS Bedrock AgentCore Documentation
- AWS S3 Data Lake Best Practices
- Intent Classification Techniques
- Pattern Recognition in Conversational AI
- Continuous Learning in Production Systems

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-05  
**Author**: AI Assistant  
**Status**: Design Complete - Ready for Architecture Design


