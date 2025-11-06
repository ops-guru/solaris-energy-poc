# RAG Flow Explanation: Test Script & Agent Workflow

**Purpose**: Detailed explanation of what the test script and agent workflow accomplish in the RAG (Retrieval-Augmented Generation) system.

---

## Overview: The Big Picture

The goal is to prove that we can:
1. **Store knowledge** (turbine manuals) in a searchable format
2. **Retrieve relevant information** when users ask questions
3. **Generate intelligent answers** using an LLM with that retrieved context

This is the foundation for the operator assistant that will help troubleshoot turbine issues.

---

## Part 1: The Test Script (`test-rag-flow.sh`)

### What It Does

The test script is an **automated end-to-end test** that verifies the entire RAG pipeline works correctly. It's like a quality check that runs the whole system and tells you if everything is working.

### Step-by-Step Flow

#### **Step 1: Process a Test Document** (Lines 32-65)

**What happens**:
1. Creates a payload with document metadata:
   ```json
   {
     "s3_bucket": "solaris-poc-documents-<account>",
     "s3_key": "test/turbine-manual-test.pdf",
     "turbine_model": "SMT60",
     "document_type": "manual"
   }
   ```

2. **Invokes the Document Processor Lambda**:
   - The document processor receives this payload
   - For demo purposes, it creates **3 mock chunks** of text:
     - Technical specifications chunk
     - Operation procedures chunk
     - Troubleshooting guide chunk
   - Each chunk gets an **embedding** (vector representation) from Bedrock Titan
   - Chunks are **stored in OpenSearch** with metadata

**What it proves**:
- ✅ Document processor Lambda works
- ✅ Embeddings are generated successfully
- ✅ Documents are stored in OpenSearch
- ✅ Index is created/updated

**Success criteria**:
- `chunks_stored` > 0
- No errors in the response

#### **Step 2: Test Agent Workflow with Queries** (Lines 71-138)

**What happens**:
1. Waits 5 seconds for OpenSearch to index the documents (line 69)

2. **Tests 3 different queries**:
   - "How do I troubleshoot low oil pressure on SMT60?"
   - "What are the operation procedures for SMT60?"
   - "What are common issues with SMT60 turbines?"

3. For each query:
   - Creates a payload with the query and session info
   - **Invokes the Agent Workflow Lambda**
   - Parses the response
   - Extracts metrics (citations count, confidence score)
   - Displays results

**What it proves**:
- ✅ Agent workflow Lambda works
- ✅ RAG retrieval finds relevant documents
- ✅ LLM generates responses with context
- ✅ Citations are returned
- ✅ Confidence scores are reasonable

**Success criteria**:
- Citations count > 0 (documents were retrieved)
- Confidence score > 0.6 (system is confident in the answer)
- Response contains relevant information

---

## Part 2: The Agent Workflow (`handler.py`)

### What It Does

The agent workflow is the **brain** of the system. When a user asks a question, it:
1. **Searches** for relevant information in OpenSearch
2. **Retrieves** the most relevant document chunks
3. **Asks** the LLM to answer the question using that context
4. **Returns** an intelligent answer with citations

### Detailed Flow

#### **Step 1: Parse the Request** (Lines 115-137)

**What happens**:
- Extracts `session_id`, `query`, and `messages` from the event
- Handles both API Gateway format and direct Lambda invocation
- Validates that a query is provided

**Purpose**: Prepare the user's question for processing

#### **Step 2: Perform RAG Retrieval** (Lines 139-190)

**This is the "Retrieval" part of RAG**

**What happens**:

1. **Connect to OpenSearch** (lines 146-150):
   - Creates an authenticated OpenSearch client using IAM
   - Connects to the vector store

2. **Extract Turbine Model** (lines 152-162):
   - Scans the query for turbine model mentions (SMT60, SMT130, TM2500)
   - Builds a filter to narrow search to that specific model

3. **Search OpenSearch** (lines 164-173):
   - **Generates query embedding**: Converts the user's question into a vector
   - **Performs hybrid search**:
     - **Semantic search (k-NN)**: Finds documents similar in meaning
     - **Keyword search (BM25)**: Finds documents with matching keywords
   - **Applies filters**: If turbine model detected, only search that model's docs
   - **Returns top 5 results**: Most relevant document chunks

4. **Build Citations** (lines 175-182):
   - Creates citation objects with:
     - Source document name
     - Page/chunk index
     - Excerpt (first 200 chars)
     - Relevance score

**What it accomplishes**:
- ✅ Finds the most relevant information for the user's question
- ✅ Uses both semantic similarity AND keyword matching
- ✅ Filters by turbine model when specified
- ✅ Provides source attribution (citations)

**Example**:
- User asks: "How do I troubleshoot low oil pressure on SMT60?"
- System searches for: documents about "oil pressure" + "troubleshooting" + "SMT60"
- Returns: Top 5 most relevant chunks from SMT60 manuals

#### **Step 3: Build Context** (Lines 192-203)

**What happens**:
- Combines all retrieved document chunks into a single context string
- Formats as: `[Document 1 - Source: manual.pdf]\n<content>\n[Document 2...]`
- If no documents found, sets context to a message saying no docs found

**Purpose**: Prepare the retrieved information to send to the LLM

#### **Step 4: Generate LLM Response** (Lines 205-206, function at 38-105)

**This is the "Augmented Generation" part of RAG**

**What happens in `invoke_bedrock_llm`**:

1. **Build System Prompt** (lines 47-52):
   - Sets the LLM's role: "expert assistant for gas turbine operations"
   - Instructions: Use documentation context, cite sources, be honest if context doesn't help

2. **Add Conversation History** (lines 54-62):
   - Includes last 5 messages for context
   - Allows the LLM to understand follow-up questions

3. **Combine Everything** (lines 64-77):
   - **Context**: Retrieved documents from OpenSearch
   - **User Question**: Original query
   - **Instructions**: How to use the context
   - **System Message**: LLM's role and guidelines

4. **Invoke Bedrock Nova Pro** (lines 89-102):
   - Sends the combined prompt to AWS Bedrock
   - Uses Nova Pro model (`amazon.nova-pro-v1:0`)
   - Gets back a generated response

**What it accomplishes**:
- ✅ Generates intelligent answers based on retrieved context
- ✅ Maintains conversation context
- ✅ Follows instructions to cite sources
- ✅ Can handle cases where no relevant docs are found

**Example**:
```
System: "You are an expert assistant..."
Context: "[Document 1 - Source: SMT60-manual.pdf]
          Troubleshooting guide for SMT60. Common issues include 
          oil pressure warnings..."
User Question: "How do I troubleshoot low oil pressure on SMT60?"
Instructions: "Answer using the context above. Cite sources."

LLM Response: "Based on the SMT60 troubleshooting guide, low oil pressure 
               can be caused by several factors. First, check the oil 
               filter for clogs... [Source: SMT60-manual.pdf]"
```

#### **Step 5: Calculate Confidence & Build Response** (Lines 208-235)

**What happens**:

1. **Calculate Confidence Score** (lines 208-215):
   - Base score: 0.8 if docs retrieved, 0.5 if not
   - Adjusts based on average relevance score from retrieved docs
   - Scales to 0.6-0.95 range

2. **Build Response Object** (lines 217-229):
   - `session_id`: Track the conversation
   - `response`: LLM-generated answer
   - `citations`: Source documents with excerpts
   - `confidence_score`: How confident the system is
   - `turbine_model`: Detected model (if any)
   - `messages`: Updated conversation history

**Purpose**: Return a complete, structured response to the user

---

## The Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    TEST SCRIPT FLOW                          │
└─────────────────────────────────────────────────────────────┘

Step 1: Document Processing
───────────────────────────
Test Script
    ↓ (invoke Lambda)
Document Processor Lambda
    ↓ (create chunks + embeddings)
OpenSearch Vector Store
    ✅ Documents stored with embeddings


Step 2: Query Testing
─────────────────────
Test Script
    ↓ (invoke Lambda with query)
Agent Workflow Lambda
    ↓
    ├─→ Generate Query Embedding (Bedrock Titan)
    ├─→ Search OpenSearch (k-NN + BM25)
    ├─→ Retrieve Top 5 Documents
    ├─→ Build Context String
    ├─→ Invoke Bedrock Nova Pro with Context
    └─→ Generate Response + Citations
    ↓
Test Script
    ✅ Displays response, citations, confidence


┌─────────────────────────────────────────────────────────────┐
│                 AGENT WORKFLOW DETAILED FLOW                 │
└─────────────────────────────────────────────────────────────┘

User Query: "How do I troubleshoot low oil pressure?"
    ↓
[1] Parse Request
    └─→ Extract: query, session_id, messages
    ↓
[2] RAG Retrieval
    ├─→ Detect turbine model: "SMT60"
    ├─→ Generate query embedding
    ├─→ Search OpenSearch (semantic + keyword)
    ├─→ Apply filter: turbine_model="SMT60"
    └─→ Retrieve top 5 chunks
    ↓
[3] Build Context
    └─→ Combine chunks into context string
    ↓
[4] LLM Generation
    ├─→ System prompt: "You are an expert assistant..."
    ├─→ Context: "[Document 1] Troubleshooting guide..."
    ├─→ User question: "How do I troubleshoot..."
    └─→ Invoke Bedrock Nova Pro
    ↓
[5] Response
    ├─→ LLM answer: "Based on the documentation..."
    ├─→ Citations: [Source: SMT60-manual.pdf, Excerpt: ...]
    ├─→ Confidence: 0.85
    └─→ Return to user
```

---

## Key Concepts Explained

### 1. **Embeddings** (Vector Representations)

**What**: A way to convert text into numbers (vectors) that capture meaning

**Example**:
- "troubleshoot oil pressure" → `[0.23, -0.45, 0.67, ...]` (1536 numbers)
- "fix low oil warning" → `[0.25, -0.43, 0.69, ...]` (similar numbers!)
- "make a sandwich" → `[-0.12, 0.34, -0.56, ...]` (very different numbers!)

**Why it matters**: 
- Semantic search can find documents that are similar in meaning, not just exact keyword matches
- "troubleshoot oil pressure" will find documents about "fixing low oil warnings" even if they don't use the exact same words

### 2. **Hybrid Search** (Semantic + Keyword)

**Semantic Search (k-NN)**:
- Finds documents based on meaning/similarity
- Good for: "troubleshoot oil pressure" finding "fix low oil warning"
- Uses embeddings to find similar vectors

**Keyword Search (BM25)**:
- Finds documents based on exact word matches
- Good for: Finding specific technical terms, model numbers, part numbers
- Uses traditional text matching with fuzzy matching

**Why both**: 
- Semantic catches conceptual matches
- Keyword catches exact term matches
- Together they provide better results

### 3. **RAG (Retrieval-Augmented Generation)**

**Traditional LLM**:
- User: "How do I troubleshoot low oil pressure?"
- LLM: "Low oil pressure can be caused by..." (generic knowledge, may be wrong)

**RAG-Enhanced LLM**:
- User: "How do I troubleshoot low oil pressure?"
- System: Searches turbine manuals → Finds relevant sections
- LLM: "Based on the SMT60 troubleshooting guide, low oil pressure can be caused by..." (specific, accurate, cites sources)

**Benefits**:
- ✅ Answers are based on actual documentation
- ✅ Can cite sources (users can verify)
- ✅ Won't hallucinate information
- ✅ Stays up-to-date (just update the docs)

### 4. **Confidence Score**

**What**: A number (0.0 - 1.0) indicating how confident the system is in its answer

**Factors**:
- Number of documents retrieved (more = better)
- Relevance scores of retrieved documents (higher = better)
- Whether any documents were found at all

**Use cases**:
- Low confidence (< 0.6): System might warn user that answer may not be accurate
- High confidence (> 0.8): System is confident in the answer

---

## What Success Looks Like

### Successful Test Run Output:

```
🧪 Testing RAG Flow for Solaris Energy POC
==========================================

Step 1: Processing test document...
✅ Document processor invoked successfully
Chunks stored: 3

Step 2: Testing agent workflow with query...

Query: How do I troubleshoot low oil pressure on SMT60?
✅ Agent workflow invoked successfully

Response: {
  "session_id": "test-session-1234567890",
  "response": "Based on the SMT60 troubleshooting guide, low oil pressure 
               can be addressed by checking the oil filter, verifying oil 
               levels, and inspecting the oil pump...",
  "citations": [
    {
      "source": "test/turbine-manual-test.pdf",
      "excerpt": "Troubleshooting guide for SMT60. Common issues include 
                  oil pressure warnings...",
      "relevance_score": 0.87
    }
  ],
  "confidence_score": 0.85,
  "turbine_model": "SMT60"
}

Metrics:
  Citations: 1
  Confidence: 0.85
✅ RAG retrieval working - found 1 citations
```

---

## Why This Matters

This RAG flow is the **foundation** for the operator assistant:

1. **Accurate Answers**: Based on actual documentation, not generic knowledge
2. **Source Attribution**: Users can verify information
3. **Model-Specific**: Can filter by turbine model (SMT60, SMT130, etc.)
4. **Scalable**: Just add more documents to expand knowledge
5. **Maintainable**: Update documents to keep answers current

Once this works, we can:
- Process real turbine manuals
- Improve chunking strategies
- Add more sophisticated search
- Migrate to AgentCore for better orchestration
- Add learning from user sessions

---

## Troubleshooting

If the test script fails:

1. **No citations returned**:
   - Check if documents were stored (Step 1)
   - Check OpenSearch connectivity
   - Check IAM permissions

2. **Low confidence scores**:
   - May indicate poor document matches
   - Try different queries
   - Verify documents contain relevant information

3. **Generic LLM responses**:
   - Check if context is being passed to LLM
   - Verify OpenSearch search is working
   - Check Bedrock model access

---

**This RAG flow proves the system can understand questions, find relevant information, and generate intelligent answers. Once proven, we'll migrate to AgentCore for production-grade orchestration.**

