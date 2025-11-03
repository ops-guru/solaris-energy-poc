# Solaris Energy Turbine Manuals

This directory contains publicly available technical documentation for the Solaris Energy Infrastructure turbine fleet, collected for the AWS AgentCore POC knowledge base.

## Overview

These manuals will be processed into a vector database (OpenSearch) for use in the operator assistant chatbot's RAG (Retrieval-Augmented Generation) pipeline.

## Directory Structure

```
manuals/
├── SMT60-Taurus60/         # 5.7 MW Mobile Power Solution
│   ├── technical-specs/    # Performance specifications, data sheets
│   ├── operational/        # Operating procedures, startup guides
│   ├── reference/          # Reference materials, OEM documentation
│   └── safety/             # Safety procedures, warnings
├── SMT130-Titan130/        # 16.5 MW Mobile Power Solution
├── TM2500-LM2500/          # 35 MW Mobile Power Solution
├── BESS/                   # Battery Energy Storage System documentation
└── general/                # Company-wide materials, handbooks
```

## Current Collection Status

- **Total Documents**: 13 PDFs downloaded successfully
- **Total Size**: ~90 MB
- **Download Date**: 2025-10-31
- **Success Rate**: 13/14 (92.8%)

### Failed Downloads

1. `Fire_Hazards_BESS_Hartford.pdf` - Connection timeout/HTTP/2 error

## Document Sources

### Solaris Energy Infrastructure
- Official technical specifications for all three turbine models
- Investor presentations (business context)

### Solar Turbines (Caterpillar)
- Taurus 60 specifications
- Product handbook for power generation

### General Electric Vernova
- LM2500+G4 technical reference (GER-4250)
- Training manuals and pocket guides
- Datasheets

### Third-Party Sources
- Training materials from MSCN7 and VBR Turbine Partners
- Safety documentation from BakerRisk
- Spec sheets from equipment suppliers

## Next Steps

1. **S3 Upload**: These PDFs will be uploaded to S3 bucket for processing
2. **Document Processing**: Lambda function will parse PDFs with hierarchical chunking
3. **Embedding Generation**: Bedrock Titan Embeddings will create vector representations
4. **Indexing**: Vector embeddings stored in OpenSearch for RAG retrieval
5. **Quality Validation**: Test retrieval accuracy with sample queries

## Notes

- All documents are publicly available and downloaded from official sources
- Proprietary OEM manuals (operator, maintenance, troubleshooting) are NOT included as they require customer portal access
- Document gaps should be supplemented with synthesized examples for POC
- Future phases may include proprietary documentation through Solaris partnership

## Manifest

See `manifest.json` for detailed metadata on each document, including:
- File paths and sizes
- Source URLs and acquisition timestamps
- Turbine model associations
- Document type classifications
- Status and error details

## Git Policy

PDF files are excluded from git via `.gitignore` due to file size. Only:
- `manifest.json` - Document metadata
- `README.md` - This file
- Directory structure

PDFs will be uploaded to S3 and managed there.

