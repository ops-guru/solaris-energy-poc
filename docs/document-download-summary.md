# Document Download Summary

**Date**: 2025-10-31  
**Purpose**: Collect publicly available turbine documentation for AWS AgentCore POC knowledge base

## Summary

✅ **Successfully Downloaded**: 13 out of 14 PDF documents (~94.75 MB)  
❌ **Failed**: 1 document (Hartford BESS Fire Hazards PDF)

## Documents by Turbine Model

### SMT60 / Taurus 60 (5.7 MW)
1. **Solaris SMT60 Technical Specs** (1.03 MB) - Official Solaris specifications
2. **Solar Taurus 60 Spec Sheet** (3.47 MB) - OEM specification sheet from Aaron Equipment

### SMT130 / Titan 130 (16.5 MW)
3. **Solaris SMT130 Technical Specs** (1.45 MB) - Official Solaris specifications

### TM2500 / LM2500+G4 (35 MW)
4. **Solaris TM2500 Technical Specs** (11.91 MB) - Official Solaris specifications
5. **LM2500G4 Datasheet** (0.56 MB) - GE Aerospace datasheet
6. **LM2500 Training Manual** (50.69 MB) - Comprehensive GE training manual
7. **GER-4250 LM2500G4 Technical Reference** (0.85 MB) - GE Vernova technical reference
8. **LM2500 Training Course Info** (0.23 MB) - VBR Turbine Partners training info
9. **LM2500 Pocket Guide** (7.0 MB) - Reference pocket guide

### General / Company-Wide
10. **SEI Investor Presentation Aug 2025** (5.66 MB)
11. **SEI Investor Presentation May 2025** (5.04 MB)
12. **Solar Turbines Product Handbook** (3.66 MB) - Power generation handbook

### BESS (Battery Energy Storage)
13. **BESS Incidents & Risk Management** (2.51 MB) - BakerRisk white paper

### Failed Downloads
14. ❌ **Fire Hazards BESS Hartford PDF** - Connection timeout/HTTP/2 error after 3 retry attempts

## Key Findings

### Coverage Analysis

**✅ Strong Coverage:**
- All three turbine models have technical specifications
- Good coverage for LM2500+G4 (6 documents including comprehensive training manual)
- Company business context documents for understanding Solaris's strategy
- BESS safety documentation

**⚠️ Known Gaps:**
- **No proprietary OEM manuals** (Operator, Maintenance, Troubleshooting) - requires Solaris customer portal access
- No Solar Turbines proprietary documentation for Taurus 60/Titan 130
- Limited procedural/operational documents (mostly reference materials)
- No Illustrated Parts Catalogs (IPCs)
- One BESS safety document failed to download

### Document Quality

**High Quality:**
- Official Solaris technical specifications (primary source)
- Comprehensive GE training manual (50+ MB, detailed operational procedures)
- OEM datasheets and technical references

**Supplementary:**
- Third-party training materials and spec sheets
- Investor presentations (provide business context)

## Recommended Next Steps

### Immediate (Phase 1-2)
1. ✅ Upload PDFs to S3 bucket
2. ✅ Process documents with hierarchical chunking
3. ✅ Generate embeddings with Bedrock Titan
4. ✅ Test retrieval accuracy with sample queries

### Future Enhancements
1. **Acquire Proprietary Documentation** - Engage with Solaris to access OEM customer portals for:
   - Operator Manuals
   - Maintenance Manuals  
   - Troubleshooting Guides
   - Illustrated Parts Catalogs

2. **Supplement Gaps** - Create synthesized examples for:
   - Common troubleshooting procedures
   - Standard operating procedures
   - Component identification guides

3. **Expand Balance of Plant** - Add documentation for:
   - Batteries
   - Transformers
   - Switchgear
   - SCR emissions systems

## Technical Details

### Download Script
- **Location**: `scripts/download_manuals.sh`
- **Method**: Bash script with curl, 3-retry logic
- **Output**: Organized directory structure by turbine model and document type

### Directory Structure
```
manuals/
├── SMT60-Taurus60/technical-specs/
├── SMT60-Taurus60/reference/
├── SMT130-Titan130/technical-specs/
├── TM2500-LM2500/technical-specs/
├── TM2500-LM2500/operational/
├── TM2500-LM2500/reference/
├── BESS/safety/
├── general/reference/
├── manifest.json
└── README.md
```

### File Organization
- PDFs excluded from git (via `.gitignore`)
- `manifest.json` contains detailed metadata
- README documents collection purpose and gaps
- Prepared for S3 upload and RAG processing

## Validation

All successfully downloaded PDFs were verified:
- File sizes match expected ranges
- Files are valid PDFs (can be opened)
- Organized in proper directory structure
- Metadata documented in manifest.json

---

**Status**: ✅ Phase 0.0 Complete - Documents ready for knowledge base construction

