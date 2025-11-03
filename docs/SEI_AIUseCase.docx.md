# Solaris Energy Infrastructure AI Use Case for Vendor Evaluation

# Use Case Overview

## Problem Statement

Solaris Energy Infrastructure specializes in renting natural gas turbines for power generation in the oil and gas industry. Turbine operators often face challenges in troubleshooting issues (e.g., nitrogen supply pressure errors, vibration anomalies) due to manual searches through technical manuals, leading to extended downtime and inefficiencies. We seek an AI solution using a Large Language Model (LLM) to provide real-time, step-by-step guidance for operators by querying an internal knowledge base of turbine manuals.

## Key Requirements

**Core Functionality**: The LLM must act as a troubleshooting assistant, allowing operators to input queries (e.g., "Guide me through fixing a nitrogen supply pressure error on XTG24920 turbine") and receive accurate, context-aware responses drawn exclusively from Solaris's turbine manuals (PDFs, text files, or structured data).

**Data Residency**: All data, including manuals and any derived knowledge base, must remain entirely within Solaris's tenants (e.g., AWS, Snowflake). Solutions requiring data ingestion, training, or processing in the vendor's tenant are ineligible.

**Integration**: Compatible with existing systems like Solaris Pulse via API. Support for natural language prompting.

**Model Preference**: Ideally, the solution would utilize Grok as the underlying LLM model for enhanced accuracy, integration with the xAI ecosystem, andalignment with Solaris's strategic focus on innovative AI tools.

User Workflow

1. Operator encounters an issue (e.g., via sensor alert).  
2. Queries the LLM: "Troubleshoot vibration spike per GT manual."  
3. LLM retrieves relevant manual sections, provides step-by-step guidance, and suggests next actions (e.g., generate API call to ServiceMax for work order).  
4. Operator provides feedback to refine responses (e.g., thumbs up/down for accuracy).

**Scope Limitations**: Focus solely on manual-based troubleshooting. Preventative maintenance (e.g., predictive analytics) will be evaluated in a future phase once turbines are fully online.

## Expected Outcomes

Faster resolution of turbine issues, reducing downtime by 20-30%.

Improved operator efficiency without requiring advanced technical skills.

Secure, compliant solution aligned with NIST cybersecurity and EPA standards.

## Measurable KPIs for Evaluation

Vendors will be assessed during a POC based on the following KPIs. Provide evidence (e.g., logs, demos) for each metric.

**Accuracy**: 95%+ relevance and correctness of LLM responses to manual-based queries (tested on 20 sample scenarios, e.g., pressure regulator fixes).

**Response Time**: \<10 seconds for query-to-guidance output; \<2 minutes for complex troubleshooting paths.

**Data Residency Compliance**: 100% confirmation that no data leaves Solaris tenants (verified via audits and architecture diagrams).

**Usability**: 90%+ satisfaction from 10 turbine operators in POC testing (via surveys on ease of prompting and guidance clarity).

**Integration Success**: Seamless connection to Solaris Pulse via API for work order generation in 80%+ of test cases.

**Scalability**: Handles queries for 50+ turbines simultaneously without performance degradation.

**Security**: Granular access controls (e.g., role-based for operators); zero vulnerabilities in POC security scan.

**Cost-Effectiveness**: Projected ROI within 6-12 months (e.g., based on downtime savings); transparent pricing for deployment and maintenance.

**Overall Success Threshold**: Achieve 85%+ across all KPIs to advance to full implementation.