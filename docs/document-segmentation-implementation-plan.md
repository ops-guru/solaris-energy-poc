# Document Segmentation Implementation Plan

## Purpose
- Establish a tagging strategy that leverages existing S3 folder hierarchy so admins only manage folders and filenames.
- Ensure all documents indexed in OpenSearch carry consistent metadata for filtering by system, subsystem, and content type.
- Provide a repeatable process for backfilling existing documents and onboarding new ones.

## Overview
- Use deterministic parsing of S3 keys to derive document metadata (facets such as `system_type`, `component`, `content_type`, `site`).
- Store parsed facets as `keyword` fields in OpenSearch alongside the raw text content.
- Maintain the original S3 key and parser version in the index so taxonomy changes can be replayed without manual tagging.
- Offer optional overrides via colocated metadata files when special cases arise.

## Folder Naming Convention
- S3 paths follow `/<project>/<system>/<component>/<content>/<filename>`.
- Example: `/projects/solar-farm-x/turbine/gearbox/maintenance/manual.pdf`
  - `project=projects/solar-farm-x`
  - `system_type=turbine`
  - `component=gearbox`
  - `content_type=maintenance`
- Optional additional depth (`location`, `site`, etc.) can map to extra facets; update the parser config to recognize new segments.
- Enforce lowercase, dash-separated tokens. Spaces should be avoided; ingestion replaces spaces with dashes if encountered.

## Ingestion Pipeline Steps
1. **Trigger**: S3 event notification (or scheduled batch crawler) sends the object key and metadata to the ingest service.
2. **Parse key**:
   - Split key on `/`, ignore empty segments.
   - Apply mapping rules (e.g., segment index → facet, lookup tables for aliases like `batteries` → `battery`).
   - Validate against schema; if mismatched, flag for review and skip ingest until corrected.
3. **Load content**:
   - Retrieve the object from S3.
   - Run existing document processing (text extraction, chunking) unchanged.
4. **Compose document record**:
   - Include facets (`system_type`, `component`, `content_type`, etc.) as arrays of keywords.
   - Add `s3_key`, `parser_version`, `ingested_at`, and `checksum` fields.
5. **Index to OpenSearch**:
   - Use `keyword` type for facet fields to support filtering and aggregations.
   - Retain existing full-text fields for search relevance.
6. **Error handling**:
   - Send validation failures to an SNS/SQS queue for manual review.
   - Surface metrics (number of skipped docs, new facets encountered) via CloudWatch.

## Backfilling Current Documents (13 docs)
1. Export existing keys from the current index or S3 listing.
2. Run the parser in batch mode to generate facet metadata.
3. Create a new OpenSearch index (`documents_v2`) with the updated mapping.
4. Bulk ingest the processed records.
5. Decommission or alias the old index to the new one once validated.

## Implementation Plan
- **Week 1**: Finalize facet schema and mapping rules; write parser library with unit tests.
- **Week 2**: Integrate parser into the existing ingest lambda/service; add structured logging and metrics.
- **Week 3**: Execute backfill for existing documents; validate index counts, sample queries, and facet filters in the UI.
- **Week 4**: Roll out monitoring dashboards and admin validation tooling (simple CLI or UI banner highlighting invalid keys).

## Operational Considerations
- Document the naming convention in the admin runbook; provide examples for each system type.
- Add a nightly job that scans S3 for keys not matching the pattern and reports them.
- Store parser rules in a versioned config (JSON/YAML) so taxonomy updates are non-code deployments.
- Future enhancement: append NLP-based topic classification to enrich search results without changing the folder-driven workflow.
