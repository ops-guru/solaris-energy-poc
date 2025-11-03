

# **Fleet Analysis and Knowledge Base Blueprint for Solaris Energy Infrastructure's Power Solutions Division**

## **Part I: Strategic Overview and Supplier Landscape**

This section provides the foundational context for developing a generative AI knowledge base for Solaris Energy Infrastructure operators. It clarifies the key corporate entities involved, analyzes the high-stakes operational environment in which the company's turbine fleet is deployed, and establishes the business drivers that will ultimately shape the nature and priority of operator queries.

### **1.1. Executive Summary**

This report delivers a comprehensive analysis of the gas turbine fleet operated by **Solaris Energy Infrastructure, Inc. (NYSE: SEI)**, the designated entity for the Generative AI Proof of Concept (POC). The primary objective is to furnish a detailed blueprint for the construction of a technical knowledge base that will empower field operators through an intelligent, query-based AI assistant.

A foundational finding of this analysis is the critical distinction between Solaris Energy Infrastructure, the operator of mobile power solutions, and **Solar Turbines**, a subsidiary of Caterpillar Inc. and a primary Original Equipment Manufacturer (OEM). Solaris Energy Infrastructure is a customer that deploys equipment sourced from Solar Turbines and other major OEMs. This distinction is paramount for the accurate sourcing of technical documentation.

The Solaris Energy Infrastructure power fleet is comprised of three core mobile solutions, which are based on turbine models from two of the world's leading OEMs: Solar Turbines and General Electric (GE).

**Table 1.1: Solaris Energy Infrastructure Turbine Fleet Summary**

| Solaris Designation | Power Rating (ISO) | Core Turbine Model | Original Equipment Manufacturer (OEM) |
| :---- | :---- | :---- | :---- |
| SMT60 | 5.7 MW | Taurus™ 60 | Solar Turbines (A Caterpillar Company) |
| SMT130 | 16.5 MW | Titan™ 130 | Solar Turbines (A Caterpillar Company) |
| TM2500 | 35 MW | LM2500+G4 | General Electric (GE Vernova) |

The company is in the midst of a significant strategic transformation, pivoting from its legacy oilfield logistics business, which has faced market deterioration, toward a high-growth "Power as a Service" model.1 This new focus primarily targets the nascent and exceptionally demanding AI data center market, which requires unprecedented levels of power reliability and quality.3

This operational context imposes extreme demands on the equipment and its operators. The GenAI knowledge base must be architected to support queries related to achieving and maintaining extreme reliability (a stated goal of 99.999% uptime), managing highly variable electrical loads characteristic of AI processing, ensuring fuel flexibility in diverse field environments, and adhering to strict emissions controls.3

To this end, this report provides a detailed dossier for each of the three primary turbine models in the Solaris fleet. Each dossier includes a technical profile synthesized from manufacturer and operator specifications, alongside an exhaustive list of potential reference materials. These lists serve as an actionable checklist for the data acquisition phase of the POC, forming the essential groundwork for a robust and effective knowledge base.

### **1.2. Clarification of Entities: Identifying the Correct "Solaris"**

A crucial first step in constructing an accurate knowledge base is to precisely identify the target organization and distinguish it from other entities with similar names. The user query's reference to "Solaris Energy" corresponds to several distinct companies, but the research definitively identifies the subject of this POC as **Solaris Energy Infrastructure, Inc.**.8 This is a publicly traded company (NYSE: SEI) headquartered in Houston, Texas, which provides mobile power generation and logistics solutions to the American energy and, increasingly, the data center industries.1

The most significant source of potential confusion is **Solar Turbines**. This entity is a key supplier to Solaris Energy Infrastructure, not the operator itself. Solar Turbines is a wholly-owned subsidiary of Caterpillar Inc. and is a global leader in the design and manufacture of industrial gas turbines within the 1-39 megawatt range.11 Therefore, Solaris Energy Infrastructure is a *customer* that purchases and operates turbine packages from Solar Turbines. Documentation from Solar Turbines is essential, but it must be understood as OEM-level material for equipment operated by Solaris Energy Infrastructure.

Other entities bearing the "Solaris" name are not relevant to this project and their documentation must be actively excluded to prevent contamination of the knowledge base. These include:

* **Solaris Energy:** A company focused on commercial solar financing and partnerships.12  
* **Solaris Energy Capital:** A private investment firm focused on midstream energy.14  
* **Solaris-Shop.com:** An online retailer of components for residential and commercial solar panel installations, such as inverters, racking, and batteries.15  
* **Solaris Energy Inc.:** A provider of solar panel installation services.17

Establishing this clear boundary is the critical first step. The GenAI knowledge base must be built exclusively from documentation relevant to Solaris Energy Infrastructure, Inc. and the specific gas turbine models it operates.

### **1.3. Operational Context: A High-Stakes Pivot to Powering the AI Revolution**

Understanding the business context of Solaris Energy Infrastructure is not merely background information; it is essential for predicting the types of questions operators will ask and for structuring the knowledge base to provide maximum value. The company is not simply growing a business line but is executing a fundamental strategic pivot critical to its long-term viability.

The company's legacy business, Solaris Logistics Solutions, which provides equipment for oil and natural gas well completions, experienced five consecutive quarters of declining revenues through the end of 2023, signaling a deteriorating market.1 In response, Solaris announced the acquisition of Mobile Energy Rentals LLC ("MER") in July 2024, which was subsequently rebranded as the "Solaris Power Solutions" segment.1 This segment has become the company's primary growth engine and is projected to account for over 80% of its consolidated Adjusted EBITDA once its full fleet of ordered turbines is deployed.2

The principal driver for this strategic shift is the explosive and unprecedented demand for power from the AI industry. Solaris Power Solutions is explicitly providing "utility scale, behind the meter power for an AI Supercluster," with contracts already in place for over 450 MW at a single location and an additional 900 MW at a new site.3 This is not a secondary market but the core of the company's future strategy.

This focus on AI data centers imposes a set of extreme operational demands. AI workloads require power infrastructure with characteristics far exceeding those of traditional data centers, including:

* **Extreme Power Density:** Modern AI racks can demand up to 80kW of sustained power, a tenfold increase over conventional servers.21  
* **Massive Scale:** A single large AI training site can require power on the scale of a nuclear reactor, with demand potentially reaching 1 GW.22  
* **Exceptional Power Quality and Reliability:** AI hardware is highly sensitive to power anomalies like voltage fluctuations and frequency deviations.24 To meet this need, Solaris contractually promises its clients **99.999% uptime**.3 This "five nines" standard of reliability is an exceptionally stringent service level agreement that leaves virtually no margin for error.

Solaris delivers on this promise through a "Power as a Service" model, providing a fully managed, turnkey solution. The company designs, rapidly deploys, operates, and maintains the entire power generation infrastructure. This scope extends beyond the gas turbines to include all necessary "balance of plant" equipment, such as transformers, switchgear, control software, batteries, and emissions control systems like Selective Catalytic Reduction (SCR) units.3

The implications of this context for the GenAI assistant are profound. The world of a Solaris field operator is defined by the relentless pressure to maintain uptime and avert crises. Any downtime directly threatens the company's core value proposition and its financial stability. Consequently, operator queries will be heavily skewed towards immediate problem resolution and proactive prevention. The AI assistant must function as a first-line-of-defense troubleshooting partner, capable of providing rapid, accurate, and actionable information to resolve alarms, diagnose performance deviations, and guide corrective actions. Its primary value lies not in retrieving general facts, but in accelerating the resolution of time-sensitive operational issues.

Furthermore, because Solaris provides a complete, integrated power solution, an operator's challenges may not originate within the gas turbine itself. A fault could lie within an ancillary component like a circuit breaker, a battery storage unit, or the SCR emissions system. While the POC will rightly focus on the turbines, the system architecture must be designed with the future in mind, capable of expanding to incorporate documentation for this entire ecosystem of "balance of plant" equipment. To be truly effective in the long term, the AI assistant must understand the *system*, not just the turbine.

Finally, the equipment is explicitly mobile and designed for rapid deployment in diverse and often rugged environments.28 Solaris employs a team of 200 field service technicians who need immediate access to information, likely via a mobile device, while on-site.31 They cannot afford to sift through cumbersome PDF documents during a critical event. This reality underscores the need for a GenAI solution that delivers concise, direct answers with clear references, highlighting the importance of properly chunking and indexing the source documents for effective semantic search and retrieval.

## **Part II: Turbine Fleet Dossier**

This section presents a detailed breakdown of each of the three core gas turbine models that constitute the Solaris Power Solutions fleet. Each of the following dossiers is designed to serve as a self-contained reference guide for the POC team, identifying the specific equipment and the universe of documentation required to build a comprehensive knowledge base for it.

### **2.1. Dossier 1: 5.7 MW Mobile Power Solution (SMT60)**

#### **2.1.1. OEM & Core Model Identification**

The 5.7 MW power solution is designated by Solaris Energy Infrastructure as the **SMT60**.29 Technical specifications and product literature from Solaris explicitly state that this unit is "Powered by Solar® Taurus™ 60 Gas Turbine".5 The Original Equipment Manufacturer (OEM) for the Taurus 60 is **Solar Turbines**, a Caterpillar company.11 The Taurus 60 is a mature and widely adopted industrial gas turbine, having been introduced in 1987 with a fleet of over 2,000 units sold and more than 300 million collective operating hours, making it a proven industry standard.32

#### **2.1.2. Technical Profile**

The SMT60 is a fully integrated, mobile power solution designed for rapid deployment and reliable operation.

* **Power Output:** The unit is rated for **5.7 MW** at ISO (International Organization for Standardization) conditions.5  
* **Heat Rate:** The Solaris technical specification for the SMT60 package lists a heat rate of **9,800 btu/kW-hr**.5 This is more efficient than the base OEM specification of 10,830 Btu/kW-hr for a standard Taurus 60 generator set.34 This discrepancy suggests that Solaris's custom packaging, which may include optimized inlet and exhaust systems or other enhancements, results in improved overall package efficiency.  
* **Fuel System:** The package is engineered for wide fuel flexibility, capable of operating on field gas, compressed natural gas (CNG), and liquefied petroleum gas (LPG). When operating on natural gas, its consumption is rated at 9.8 standard cubic feet per kilowatt-hour (scf/kW-hr).5 The core Taurus 60 engine is available with Solar Turbines' SoLoNOx™ (Dry Low Emission) combustion system, which reduces emissions without the need for water or steam injection.35  
* **Emissions:** The SMT60 package is designed as a low-emissions system, with Nitrogen Oxides (NOx) rated at **9 parts per million (ppm)** and Carbon Monoxide (CO) at less than 2 ppm.5  
* **Key Features:** The defining feature of the SMT60 is its mobility and speed of deployment. It is configured as a single-trailer mobile unit designed to "Park, plug and power" with a setup time of less than four hours, requiring no concrete foundation or crane lifts.5 The package is self-contained, incorporating utility-grade switchgear, a protective relay module, a complete electrical equipment compartment with a motor control center (MCC), and enhanced sound attenuation to achieve a noise level of 85 dBA at 5 feet.5

#### **2.1.3. Identified Reference Materials for Knowledge Base**

Acquiring the following documents is the primary objective of the data collection phase for the SMT60. The most critical manuals are proprietary and will require direct engagement with Solaris Energy Infrastructure to access via the OEM's customer portal.

**Table 2.1: Documentation Checklist for Solar Turbines Taurus™ 60**

| Document Type | Description & Relevance | Likely Source & Snippet Evidence |
| :---- | :---- | :---- |
| **Technical Data Sheet (TDS)** | Provides top-level performance specifications, dimensions, fuel consumption, emissions data, and key package features. Essential for establishing the baseline knowledge of the unit. | **Public:** Available as a downloadable PDF from the Solaris Energy Infrastructure website.5 General specifications are also available on the Solar Turbines public website.33 |
| **Operator Manual** | The primary guide for field operators. Covers standard operating procedures (SOPs), including start-up, monitoring of critical parameters, normal shutdown, and emergency procedures. This is the **highest priority document** for the knowledge base. | **Proprietary:** Available exclusively through the Solar Turbines customer portal ("Technical Manuals" section).39 General content and scope can be inferred from technical specification documents.35 |
| **Maintenance Manual** | Details all scheduled maintenance tasks (e.g., 4,000-hour and 8,000-hour inspections), procedures for component replacement, lubrication schedules, and alignment specifications. Crucial for answering preventive and corrective maintenance queries. | **Proprietary:** Available via the Solar Turbines customer portal.39 The existence of specific maintenance procedures for alignment and Inlet Guide Vane (IGV) control is confirmed by third-party technical forums.41 |
| **Troubleshooting Guide** | Provides diagnostic logic trees and step-by-step procedures for resolving system alarms, fault codes, and performance deviations. This document is critical for enabling the GenAI's problem-solving capabilities. | **Proprietary:** Available via the Solar Turbines customer portal.39 The OEM provides extensive lifecycle support, including Field Services and Digital Solutions, which are informed by this documentation.42 |
| **Illustrated Parts Catalog (IPC)** | Contains exploded-view diagrams of all major assemblies and lists all replaceable components with their corresponding part numbers. Essential for any query related to identifying or ordering spare parts. | **Proprietary/Third-Party:** The official source is the "Shop Solar" e-commerce portal, accessible to customers.43 Third-party suppliers also list part numbers for common components and kits, providing a partial, publicly accessible view.44 |
| **Fuel Specification (ES 9-98)** | A detailed OEM engineering specification that defines the required quality, composition, and contaminant limits for all approved gaseous and liquid fuels. Critical for troubleshooting combustion issues or performance problems related to fuel quality. | **Proprietary:** This specific document number is referenced in OEM technical documents.40 It is available to customers through the Solar Turbines portal under "Bulletins, Advisories, and Specifications".39 |
| **Lube Oil Specification (ES 9-224)** | A detailed OEM engineering specification defining the required properties for lubricating oil. Essential for all queries related to lubrication system maintenance, oil analysis, and fluid replacement. | **Proprietary:** This specific document number is referenced in OEM technical documents.40 It is available to customers via the Solar Turbines portal.39 |
| **Technical Bulletins & Advisories** | Official communications from the OEM regarding product updates, newly identified issues, mandatory safety modifications, and recommended operational changes. This is vital for ensuring the knowledge base contains the most current and safety-critical information. | **Proprietary:** Available exclusively through the Solar Turbines customer portal under "Bulletins, Advisories, and Specifications".39 |

### **2.2. Dossier 2: 16.5 MW Mobile Power Solution (SMT130)**

#### **2.2.1. OEM & Core Model Identification**

Solaris Energy Infrastructure's 16.5 MW solution is designated the **SMT130**.28 This mobile power unit is explicitly "Powered by Solar® Titan™ 130 Gas Turbine".6 The OEM is **Solar Turbines**.11 The Titan 130 model was introduced in 1997 and represents a more powerful offering in the Solar Turbines portfolio, leveraging design experience from their successful Mars and Taurus product lines.47 This model is a cornerstone of Solaris's fleet expansion strategy, with the company having recently placed orders for nine additional 16.5 MW units to meet accelerating customer demand.27

#### **2.2.2. Technical Profile**

The SMT130 is a high-capacity, fully integrated mobile power solution designed for larger-scale, rapid-deployment projects.

* **Power Output:** The unit is rated for **16.5 MW** at ISO conditions.6  
* **Heat Rate:** The Solaris technical specification for the SMT130 package lists a heat rate of **9,630 btu/kW-hr**.6 This figure aligns very closely with the base OEM specification of 9,605 Btu/kWhe for a standard Titan 130 generator set, indicating a highly efficient package integration.47  
* **Fuel System:** Like the SMT60, the SMT130 offers wide fuel flexibility, including field gas, CNG, and LPG. Its natural gas consumption is rated at **8.68 scf/kW-hr**.6 The core Titan 130 engine is available with the SoLoNOx™ combustion system for low emissions.48  
* **Emissions:** The SMT130 package is rated for low emissions, with NOx at **9 ppm**, CO at less than 2 ppm, and Volatile Organic Compounds (VOC) at less than 2 ppm.6  
* **Key Features:** The SMT130 is configured as a **dual-trailer mobile unit**, with one trailer for the turbine and another for the generator.6 This modular design allows for the transport of a higher capacity unit while still enabling quick setup (less than 12 hours) without the need for a concrete foundation or major crane lifts. The package includes utility-grade switchgear, a motor control center, and HVAC systems, with optional sound attenuation available.6

#### **2.2.3. Identified Reference Materials for Knowledge Base**

The required documentation for the Titan 130 is analogous to that of the Taurus 60, as both are sourced from Solar Turbines. Access to the proprietary manuals via the OEM customer portal is equally critical for this model.

**Table 2.2: Documentation Checklist for Solar Turbines Titan™ 130**

| Document Type | Description & Relevance | Likely Source & Snippet Evidence |
| :---- | :---- | :---- |
| **Technical Data Sheet (TDS)** | Provides top-level performance specifications, dimensions for the dual-trailer setup, fuel consumption, emissions data, and key package features. | **Public:** Available as a downloadable PDF from the Solaris Energy Infrastructure website.6 General specifications are also available on the Solar Turbines public website.38 |
| **Operator Manual** | The primary guide for field operators, covering all aspects of normal operation. This is the **highest priority document** for the knowledge base. | **Proprietary:** Available exclusively through the Solar Turbines customer portal.39 The existence of comprehensive documentation is confirmed in general product handbooks and case studies.49 |
| **Maintenance Manual** | Details all scheduled maintenance tasks, inspection criteria, and procedures for component replacement. | **Proprietary:** Available via the Solar Turbines customer portal.39 References to Operation and Maintenance Manuals are made in various OEM documents, confirming their availability to customers.51 |
| **Troubleshooting Guide** | Provides diagnostic logic and step-by-step procedures for resolving system alarms and faults. | **Proprietary:** Available via the Solar Turbines customer portal.39 The OEM's direct support services are the primary channel for complex troubleshooting.54 |
| **Illustrated Parts Catalog (IPC)** | Contains diagrams and part numbers for all replaceable components. | **Proprietary/Third-Party:** The official source is the "Shop Solar" e-commerce portal.43 Third-party suppliers provide lists of parts for scheduled maintenance kits (e.g., 4,000 and 8,000-hour kits), offering a glimpse into the catalog.51 |
| **Technical Bulletins & Advisories** | Official OEM communications regarding product updates, known issues, and mandatory modifications. | **Proprietary:** Available exclusively through the Solar Turbines customer portal under "Bulletins, Advisories, and Specifications".39 |

### **2.3. Dossier 3: 35 MW Mobile Power Solution (TM2500)**

#### **2.3.1. OEM & Core Model Identification**

The 35 MW power solution offered by Solaris Energy Infrastructure is designated the **TM2500**.26 The company's product literature explicitly states this unit is "Powered by GE® LM2500+G4 Gas Turbine".7 The OEM is **General Electric (GE)**, with its gas power division now part of **GE Vernova**.57 The LM2500 is a globally recognized aeroderivative gas turbine, a design derived from GE's successful CF6 aircraft engine. This lineage provides benefits such as high power density and reliability, and the engine has a long and successful history in industrial power generation and marine propulsion.58

#### **2.3.2. Technical Profile**

The TM2500 is the highest-capacity mobile offering in the Solaris fleet, designed for applications where speed of deployment and scalability are critical.

* **Power Output:** The unit is rated for **35 MW**.7 This is consistent with the base GE rating of approximately 37 MW, with the final output being dependent on specific site conditions such as ambient temperature and altitude.57  
* **Heat Rate / Efficiency:** The Solaris technical specification lists a heat rate of **9,189 Btu/kW-hr (LHV)** at 32°F, which corresponds to a thermal efficiency of approximately **37.2%**.7 This high efficiency is a key characteristic of aeroderivative turbines.  
* **Fuel System:** The package is configured for dual-fuel capability, able to operate on natural gas (including CNG and LNG) and Diesel \#2 liquid fuel. It utilizes water injection for NOx control when operating on liquid fuel.7 The core LM2500+G4 engine platform has extensive fuel flexibility and has been operated on fuels with high hydrogen content.57  
* **Emissions:** The TM2500 package is rated for low emissions, with NOx at **9 ppm**, CO at less than 2 ppm, and VOC at less than 2 ppm.7  
* **Key Features:** The TM2500 is packaged in a compact, trailer-mounted configuration designed for rapid deployment, with a stated **12-hour setup time**.7 The LM2500 family is renowned for its fast-start capability, able to go from a cold state to full load in as little as 5 minutes, a critical feature for providing backup power or capitalizing on favorable grid pricing.57 The package includes onboard switchgear, protective relays, and a low-voltage transformer for auxiliary power.7

#### **2.3.3. Identified Reference Materials for Knowledge Base**

Documentation for the GE LM2500+G4 will be sourced through GE Vernova's channels. As with Solar Turbines, the most detailed operational and maintenance manuals are proprietary and require customer-level access.

**Table 2.3: Documentation Checklist for GE LM2500+G4**

| Document Type | Description & Relevance | Likely Source & Snippet Evidence |
| :---- | :---- | :---- |
| **Technical Data Sheet (TDS)** | Provides top-level performance specifications, dimensions, fuel capabilities, emissions data, and key package features. | **Public:** Available as a downloadable PDF from the Solaris Energy Infrastructure website.7 General specifications are also available on the GE Vernova public website.57 |
| **Operator Manual** | The primary guide for field operators, covering all aspects of normal operation, including control system interface and monitoring. This is the **highest priority document** for the knowledge base. | **Proprietary:** Available through the GE customer portal. The comprehensive scope of these manuals is detailed in third-party training course outlines and specific system description documents that have become publicly available.58 |
| **Maintenance Manual** | Details all scheduled maintenance tasks based on OEM standards (e.g., GE's GER 3620 bulletin), inspection criteria, and major component repair procedures. | **Proprietary:** Available via the GE customer portal. The existence of specific maintenance manuals, such as "GEK LM2500 PK," and troubleshooting pocket guides is confirmed by various sources.64 |
| **Troubleshooting Guide** | Provides diagnostic logic and step-by-step procedures for resolving common issues such as lube system leaks, high vibration alarms, and post-shutdown restart lockouts. | **Proprietary:** Available via the GE customer portal. Detailed troubleshooting flowcharts and procedures are documented.64 Community forums also provide valuable context on real-world troubleshooting scenarios.67 |
| **Illustrated Parts Catalog (IPC)** | Contains diagrams and part numbers for all replaceable components. | **Proprietary/Third-Party:** The official source is the GE customer portal. Third-party maintenance providers like VBR Turbine Partners and MTU Maintenance also list available spare parts, providing a partial public view of the catalog.69 |
| **Technical Bulletins & Advisories** | Official OEM communications regarding product updates, known issues, and mandatory modifications. | **Proprietary:** Available exclusively through the GE customer portal. |
| **Installation & Commissioning Manual** | Provides detailed procedures for site setup, initial testing, and commissioning. This can be valuable for troubleshooting issues that arise during or shortly after deployment. | **Proprietary:** Available via the GE customer portal. The existence of a specific Installation and Commissioning Manual is referenced in document lists.65 |

## **Part III: Knowledge Base Construction and Recommendations**

This final section synthesizes the fleet analysis into a strategic framework for constructing the GenAI knowledge base. It provides a master catalog of essential document types, outlines a tiered strategy for their acquisition, and offers initial guidance for tailoring the GenAI agent's capabilities to meet the specific needs of Solaris Energy Infrastructure's field operators.

### **3.1. Comprehensive Catalog of Essential Documentation Types**

The detailed analysis of the SMT60, SMT130, and TM2500 reveals a consistent set of documentation categories that are critical for safe, reliable, and efficient turbine operation. A comprehensive knowledge base must include materials from each of the following categories, which are organized here by the primary need-state of the operator.

* **For Routine Operations & Performance Monitoring:**  
  * **Operator's Manual:** The foundational document containing step-by-step procedures for all normal operating phases, from pre-start checks to full-load operation and standard shutdown.  
  * **Control System Manual:** A detailed guide to the Human-Machine Interface (HMI) and the underlying control logic (e.g., for systems like Solar's Turbotronic™ or GE's Mark VIe). This is essential for interpreting screen data and understanding automated sequences.  
  * **Technical Data Sheets:** Quick-reference documents for key performance specifications (power output, heat rate, fuel consumption, etc.) under standard conditions.  
  * **Performance Maps:** A series of charts that illustrate the turbine's expected performance (e.g., power output, efficiency) across a range of ambient conditions, including temperature, humidity, and altitude. These are vital for operators to determine if their unit is performing as expected.  
* **For Troubleshooting & Problem Resolution:**  
  * **Troubleshooting Manual/Guide:** The most critical document for reactive situations. It should contain diagnostic flowcharts and detailed procedures for investigating specific alarm codes, fault conditions, and abnormal operational readings (e.g., high vibration, high exhaust temperature).  
  * **System Schematics (P\&IDs):** Piping and Instrumentation Diagrams for all major fluid and electrical systems, including fuel, lube oil, hydraulics, and control wiring. These are indispensable for tracing problems and understanding system interdependencies.  
  * **Technical Bulletins & Service Advisories:** Time-sensitive communications from the OEM that address known product issues, required component modifications, or updated operational procedures. These are vital for safety and reliability.  
* **For Maintenance & Repair:**  
  * **Maintenance Manual:** A comprehensive guide detailing all scheduled and unscheduled maintenance activities. This includes instructions for periodic inspections (e.g., borescope inspections), component replacement procedures, and major overhaul tasks.  
  * **Illustrated Parts Catalog (IPC):** An exhaustive catalog of all replaceable components, featuring exploded-view diagrams and precise part numbers. This is essential for correctly identifying and ordering spare parts.  
  * **Alignment Procedures:** Specific, detailed instructions for the critical task of aligning the gas turbine shaft with the driven equipment (the generator).  
  * **Fluid Specifications:** Formal engineering specifications (e.g., Solar's ES 9-98 for fuel, ES 9-224 for lube oil) that define the required chemical and physical properties for all operational fluids. Adherence to these specifications is critical for warranty and equipment longevity.

### **3.2. Data Acquisition Strategy**

A tiered approach is recommended to systematically acquire the necessary documentation for the POC.

* **Tier 1: Publicly Available Information (Immediate Action):** The project team should immediately begin to systematically download all publicly available technical documents from the Solaris Energy Infrastructure website (solaris-energy.com) and the respective OEM websites (solarturbines.com and gevernova.com). This initial dataset will primarily consist of the technical data sheets, brochures, and case studies identified in Part II.5 This will form the baseline dataset for the knowledge base.  
* **Tier 2: Third-Party and Community Sources (Supplemental Data):** The team should augment the baseline dataset by scraping relevant information from the websites of third-party parts suppliers and maintenance providers, as well as from technical community forums.41 While this information is not official OEM documentation, it provides invaluable real-world context on common failure modes, frequently replaced part numbers, and the practical challenges that operators face. This data can be instrumental in fine-tuning the GenAI's understanding of operator terminology and common problem areas.  
* **Tier 3: Proprietary OEM Documentation (Critical Path for POC Success):** The analysis conclusively shows that the most valuable and detailed documents—specifically the Operator, Maintenance, and Troubleshooting Manuals—are proprietary. They are not available on public websites but are accessible to equipment owners through secure customer portals, such as the one offered by Solar Turbines, which provides access to technical manuals, bulletins, and specifications.39  
  **Recommendation:** The success of the GenAI POC is contingent upon accessing this high-quality, proprietary data. The POC team must formally engage with their project sponsors and technical counterparts at Solaris Energy Infrastructure. As the equipment owner, Solaris will have the necessary credentials to access these OEM portals. A data-sharing agreement or the provision of direct access to the POC team for the purpose of data ingestion is the only viable path forward. Without these Tier 3 documents, the knowledge base will be critically incomplete, and the GenAI assistant will be unable to answer the most important and time-sensitive operator questions.

### **3.3. Initial Insights for GenAI Agent Training & Capabilities**

The nature of the equipment and the operational environment provides clear direction for the required capabilities of the GenAI agent.

The work of a field operator is inherently physical and procedural. Text-only answers to complex maintenance or troubleshooting questions are often insufficient. For example, a query such as, "Where is the primary fuel shutoff valve on the SMT60?" is best answered not only with a text description from the manual but also with the corresponding diagram from the Illustrated Parts Catalog that visually pinpoints the component's location. Maintenance and troubleshooting manuals are rich with schematics, diagrams, and photographs that are essential for comprehension. Therefore, the GenAI framework must be architected to be multi-modal, capable of ingesting, indexing, and presenting images and diagrams in conjunction with text-based answers. The document ingestion pipeline must be designed to extract and associate this visual information with the relevant text segments.

Furthermore, the agent must be able to discern the nuances between generic OEM specifications and Solaris's specific, integrated solutions. The analysis revealed discrepancies, such as the different heat rate specifications for the SMT60 package versus the base Taurus 60 engine.5 This is because Solaris is not merely operating a standard OEM turbine; it is deploying a custom-engineered, mobile package with its own set of ancillary systems that affect overall performance. The operator's reality is the Solaris package. Therefore, during data ingestion, documents originating from Solaris Energy Infrastructure (e.g., their technical data sheets) should be tagged with a higher priority or weighting than generic OEM brochures. The retrieval strategy must enable the GenAI to correctly answer, "What is the heat rate of *my SMT60*?" with the Solaris-specific number, while still having the ability to provide the base OEM specification if explicitly asked. This requires careful data source tagging and a sophisticated retrieval algorithm.

To guide the initial development and testing of the POC, the following categories of queries should be prioritized, as they directly reflect the anticipated needs of a field operator:

* **Procedural Queries:** "What are the steps to perform a crank wash on a Taurus 60?" or "Walk me through the startup sequence for an LM2500+G4."  
* **Troubleshooting Queries:** "What does alarm code F-123 mean on a Titan 130 control panel?" or "My vibration reading on the generator drive-end bearing is 3.6 mils; what are the possible causes and immediate actions?"  
* **Specification Queries:** "What is the maximum allowable exhaust gas temperature for the SMT130?" or "What type of lubricating oil is specified for the Taurus 60 gearbox?"  
* **Component Identification Queries:** "Show me a diagram of the fuel injector assembly for the SMT60" or "What is the part number for the backup lube oil filter on a Titan 130?"

#### **Works cited**

1. Solaris Energy Infrastructure: How A Crumbling Texas Oilfield Services Company Gambled It All On A Convicted Felon And The World's Richest Man \- Morpheus Research, accessed October 30, 2025, [https://www.morpheus-research.com/solaris-energy-infrastructure-how-a-crumbling-texas-oilfield-services-company-gambled-it-all-on-a-convicted-felon-and-the-worlds-richest-man/](https://www.morpheus-research.com/solaris-energy-infrastructure-how-a-crumbling-texas-oilfield-services-company-gambled-it-all-on-a-convicted-felon-and-the-worlds-richest-man/)  
2. Solaris Energy Soars From $8 to $28 in 2024: Can This Repeat in 2025? | Nasdaq, accessed October 30, 2025, [https://www.nasdaq.com/articles/solaris-energy-soars-8-28-2024-can-repeat-2025](https://www.nasdaq.com/articles/solaris-energy-soars-8-28-2024-can-repeat-2025)  
3. Power As A Service | Solaris Energy Infrastructure, accessed October 30, 2025, [https://www.solaris-energy.com/power](https://www.solaris-energy.com/power)  
4. Solaris Energy Infrastructure, Inc. Investor Presentation, accessed October 30, 2025, [https://ir.solaris-energy.com/\~/media/Files/S/Solaris-IR/reports-and-presentations/sei-investor-presentation-august-2025.pdf](https://ir.solaris-energy.com/~/media/Files/S/Solaris-IR/reports-and-presentations/sei-investor-presentation-august-2025.pdf)  
5. 5.7MW Turbine Power, accessed October 30, 2025, [https://irp.cdn-website.com/f809ccf0/files/uploaded/Solaris\_5.7MW\_Turbine\_Power\_-\_Tech\_Specs-243257d2.pdf](https://irp.cdn-website.com/f809ccf0/files/uploaded/Solaris_5.7MW_Turbine_Power_-_Tech_Specs-243257d2.pdf)  
6. 16.5 MW Turbine Power, accessed October 30, 2025, [https://irp.cdn-website.com/f809ccf0/files/uploaded/Solaris\_16.5MW\_Turbine\_Power\_-\_Tech\_Specs.pdf](https://irp.cdn-website.com/f809ccf0/files/uploaded/Solaris_16.5MW_Turbine_Power_-_Tech_Specs.pdf)  
7. 35 MW Turbine Power, accessed October 30, 2025, [https://irp.cdn-website.com/f809ccf0/files/uploaded/Solaris\_35MW\_Turbine\_Power\_-\_Tech\_Specs-83f9c921.pdf](https://irp.cdn-website.com/f809ccf0/files/uploaded/Solaris_35MW_Turbine_Power_-_Tech_Specs-83f9c921.pdf)  
8. Company | Solaris Energy Infrastructure, accessed October 30, 2025, [https://www.solaris-energy.com/company](https://www.solaris-energy.com/company)  
9. Solaris Energy Infrastructure | Reliable Technology, Dedicated Service, accessed October 30, 2025, [https://www.solaris-energy.com/](https://www.solaris-energy.com/)  
10. SOLARIS ENERGY INFRASTRUCTURE, INC.\_December 31, 2024 \- SEC.gov, accessed October 30, 2025, [https://www.sec.gov/Archives/edgar/data/1697500/000169750025000013/sei-20241231x10k.htm](https://www.sec.gov/Archives/edgar/data/1697500/000169750025000013/sei-20241231x10k.htm)  
11. Solar Turbines | Powering the Future, accessed October 30, 2025, [https://www.solarturbines.com/en\_US.html](https://www.solarturbines.com/en_US.html)  
12. Solar Energy Services | Solaris Energy | United States, accessed October 30, 2025, [https://www.solarisenergy.com/solar-energy-services](https://www.solarisenergy.com/solar-energy-services)  
13. Commerical Solar Financing | Solaris Energy | United States, accessed October 30, 2025, [https://www.solarisenergy.com/](https://www.solarisenergy.com/)  
14. Solaris Energy Capital: United States, accessed October 30, 2025, [https://www.solarisenergycapital.com/](https://www.solarisenergycapital.com/)  
15. Brands \- Solaris-shop.com, accessed October 30, 2025, [https://www.solaris-shop.com/brands/](https://www.solaris-shop.com/brands/)  
16. Solar Panels, Solar Panel Kits and Energy Supply \- Solaris, accessed October 30, 2025, [https://www.solaris-shop.com/](https://www.solaris-shop.com/)  
17. Solaris Energy Inc.: Home, accessed October 30, 2025, [https://www.solarisenergy-inc.com/](https://www.solarisenergy-inc.com/)  
18. Solaris-Energy-Infrastructure-Complaint.pdf \- The Law Offices Of Howard G. Smith, accessed October 30, 2025, [https://www.howardsmithlaw.com/wp-content/uploads/2025/03/Solaris-Energy-Infrastructure-Complaint.pdf](https://www.howardsmithlaw.com/wp-content/uploads/2025/03/Solaris-Energy-Infrastructure-Complaint.pdf)  
19. Solaris Energy Infrastructure, Inc. (SEI) Stock Price, Market Cap, Segmented Revenue & Earnings \- Datainsightsmarket.com, accessed October 30, 2025, [https://www.datainsightsmarket.com/companies/SEI](https://www.datainsightsmarket.com/companies/SEI)  
20. SEI Investor Presentation May 2025 \- Solaris Energy Infrastructure, accessed October 30, 2025, [https://ir.solaris-energy.com/\~/media/Files/S/Solaris-IR/reports-and-presentations/sei-investor-presentation-may-2025.pdf](https://ir.solaris-energy.com/~/media/Files/S/Solaris-IR/reports-and-presentations/sei-investor-presentation-may-2025.pdf)  
21. Power Requirements for AI Data Centers: Resilient Infrastructure, accessed October 30, 2025, [https://www.hanwhadatacenters.com/blog/power-requirements-for-ai-data-centers-resilient-infrastructure/](https://www.hanwhadatacenters.com/blog/power-requirements-for-ai-data-centers-resilient-infrastructure/)  
22. AI's Power Requirements Under Exponential Growth \- RAND, accessed October 30, 2025, [https://www.rand.org/pubs/research\_reports/RRA3572-1.html](https://www.rand.org/pubs/research_reports/RRA3572-1.html)  
23. Can US infrastructure keep up with the AI economy? \- Deloitte, accessed October 30, 2025, [https://www.deloitte.com/us/en/insights/industry/power-and-utilities/data-center-infrastructure-artificial-intelligence.html](https://www.deloitte.com/us/en/insights/industry/power-and-utilities/data-center-infrastructure-artificial-intelligence.html)  
24. Power quality: The unseen phenomenon behind some of the biggest data center challenges, accessed October 30, 2025, [https://flex.com/resources/power-quality-the-unseen-phenomenon-behind-some-of-the-biggest-data-center-challenges](https://flex.com/resources/power-quality-the-unseen-phenomenon-behind-some-of-the-biggest-data-center-challenges)  
25. Manage and analyze power quality | Data Centers \- Siemens Xcelerator Global, accessed October 30, 2025, [https://xcelerator.siemens.com/global/en/industries/data-centers/use-cases/improve-power-quality.html](https://xcelerator.siemens.com/global/en/industries/data-centers/use-cases/improve-power-quality.html)  
26. Products & Services | Solaris Energy Infrastructure, accessed October 30, 2025, [https://www.solaris-energy.com/solutions](https://www.solaris-energy.com/solutions)  
27. Solaris Energy Infrastructure Announces Fourth Quarter 2024 Financial and Operational Update and Power Solutions Growth Capital Developments, accessed October 30, 2025, [https://ir.solaris-energy.com/news/2024/12-04-2024-232917240](https://ir.solaris-energy.com/news/2024/12-04-2024-232917240)  
28. 16.5 MW Turbine Power \- Solaris Energy Infrastructure, accessed October 30, 2025, [https://www.solaris-energy.com/solutions/power/16.5-mw-turbine-power](https://www.solaris-energy.com/solutions/power/16.5-mw-turbine-power)  
29. 5.7 MW Turbine Power \- Solaris Energy Infrastructure, accessed October 30, 2025, [https://www.solaris-energy.com/solutions/power/5.7-mw-turbine-power](https://www.solaris-energy.com/solutions/power/5.7-mw-turbine-power)  
30. Industrial | Solaris Energy Infrastructure, accessed October 30, 2025, [https://www.solaris-energy.com/industry-applications/industrial](https://www.solaris-energy.com/industry-applications/industrial)  
31. Solaris Energy Infrastructure \- PTC, accessed October 30, 2025, [https://www.ptc.com/en/case-studies/solaris-energy](https://www.ptc.com/en/case-studies/solaris-energy)  
32. Solar Mobile Turbomachinery, accessed October 30, 2025, [https://www.solarturbines.com/en\_US/solutions/oil-and-gas/solar-mobile-turbomachinery.html](https://www.solarturbines.com/en_US/solutions/oil-and-gas/solar-mobile-turbomachinery.html)  
33. Taurus 60 \- Solar Turbines, accessed October 30, 2025, [https://www.solarturbines.com/en\_US/products/oil-and-gas-power-generation-packages/taurus-60.html](https://www.solarturbines.com/en_US/products/oil-and-gas-power-generation-packages/taurus-60.html)  
34. Taurus 60 \- Solar Turbines, accessed October 30, 2025, [https://www.solarturbines.com/en\_US/products/power-generation-packages/taurus-60.html](https://www.solarturbines.com/en_US/products/power-generation-packages/taurus-60.html)  
35. TAURUS 60, accessed October 30, 2025, [https://va.mite.gov.it/File/Documento/251978](https://va.mite.gov.it/File/Documento/251978)  
36. TAURUS 60, accessed October 30, 2025, [http://s7d2.scene7.com/is/content/Caterpillar/C10550209](http://s7d2.scene7.com/is/content/Caterpillar/C10550209)  
37. TAURUS 60, accessed October 30, 2025, [https://s7d2.scene7.com/is/content/Caterpillar/CM20150703-52095-49890](https://s7d2.scene7.com/is/content/Caterpillar/CM20150703-52095-49890)  
38. Power Generation \- Solar Turbines, accessed October 30, 2025, [https://www.solarturbines.com/en\_US/products/power-generation-packages.html](https://www.solarturbines.com/en_US/products/power-generation-packages.html)  
39. Customer Applications and Portals \- Lifecycle Support \- Solar Turbines, accessed October 30, 2025, [https://www.solarturbines.com/en\_US/services/customer-applications-portals.html](https://www.solarturbines.com/en_US/services/customer-applications-portals.html)  
40. Solar Taurus 60 Turbine Generators Sets \- Aaron Equipment, accessed October 30, 2025, [https://www.aaronequipment.com/equipmentattachments/11729003\_solar\_taurus\_60\_gas\_turbine\_generator.pdf](https://www.aaronequipment.com/equipmentattachments/11729003_solar_taurus_60_gas_turbine_generator.pdf)  
41. Category: Taurus 60 \- FT8 & Solar – Turbine Technical Information, accessed October 30, 2025, [https://www.dmba5411.com/category/taurus-60/](https://www.dmba5411.com/category/taurus-60/)  
42. Lifecycle Support | Solar Turbines, accessed October 30, 2025, [https://www.solarturbines.com/en\_US/services.html](https://www.solarturbines.com/en_US/services.html)  
43. Solar Turbines Parts \- Lifecycle Support, accessed October 30, 2025, [https://www.solarturbines.com/en\_US/services/parts.html](https://www.solarturbines.com/en_US/services/parts.html)  
44. Gas Turbines, Solar Turbines and Compressor parts by Antoni International \- Parts, accessed October 30, 2025, [http://www.antoni-intl.com/Parts/id/44/offset/1081/](http://www.antoni-intl.com/Parts/id/44/offset/1081/)  
45. Solar Turbines Parts \- 747 Items \- Salvex, accessed October 30, 2025, [https://www.salvex.com/listings/listing\_detail.cfm/aucid/182999003/](https://www.salvex.com/listings/listing_detail.cfm/aucid/182999003/)  
46. New Gas Turbine for Sale \- Solar® Taurus 60 Package (New, 50 Hz) | EthosEnergy, accessed October 30, 2025, [https://ethosenergy.com/parts-and-equipment/solar-taurus-60-package-4-new-50-hz](https://ethosenergy.com/parts-and-equipment/solar-taurus-60-package-4-new-50-hz)  
47. Solar Turbines \- Wikipedia, accessed October 30, 2025, [https://en.wikipedia.org/wiki/Solar\_Turbines](https://en.wikipedia.org/wiki/Solar_Turbines)  
48. Titan 130 Compressor Set \- Solar Turbines, accessed October 30, 2025, [https://www.solarturbines.com/en\_US/products/gas-compressor-packages/titan-130.html](https://www.solarturbines.com/en_US/products/gas-compressor-packages/titan-130.html)  
49. PRODUCT HANDBOOK FOR POWER GENERATION, accessed October 30, 2025, [https://mcatradeandlearn.com/wp-content/uploads/2020/11/Solar-Turbine-Produt-Handbook-for-Power-Generation.pdf](https://mcatradeandlearn.com/wp-content/uploads/2020/11/Solar-Turbine-Produt-Handbook-for-Power-Generation.pdf)  
50. Power Generation Modules \- Solar Turbines, accessed October 30, 2025, [https://www.solarturbines.com/en\_US/solutions/power-generation/power-generation-modules.html](https://www.solarturbines.com/en_US/solutions/power-generation/power-generation-modules.html)  
51. TITAN 130, accessed October 30, 2025, [http://s7d2.scene7.com/is/content/Caterpillar/C10550182](http://s7d2.scene7.com/is/content/Caterpillar/C10550182)  
52. TITAN 130: Gas Turbine Generator Set | PDF \- Scribd, accessed October 30, 2025, [https://www.scribd.com/document/272375396/ds130pg](https://www.scribd.com/document/272375396/ds130pg)  
53. Titan 130 \- Solar Turbines, accessed October 30, 2025, [https://www.solarturbines.com/en\_US/products/oil-and-gas-power-generation-packages/titan-130.html](https://www.solarturbines.com/en_US/products/oil-and-gas-power-generation-packages/titan-130.html)  
54. Titan 130 \- Solar Turbines, accessed October 30, 2025, [https://www.solarturbines.com/en\_US/products/power-generation-packages/titan-130.html](https://www.solarturbines.com/en_US/products/power-generation-packages/titan-130.html)  
55. Titan 130 Mechanical Drive Package \- Solar Turbines, accessed October 30, 2025, [https://www.solarturbines.com/en\_US/products/mechanical-drive-packages/titan-130.html](https://www.solarturbines.com/en_US/products/mechanical-drive-packages/titan-130.html)  
56. Spare Parts List Titan 130 Gas Turbine, accessed October 30, 2025, [http://gas-turbine-parts.com/News/Product\_FAQ/147.html](http://gas-turbine-parts.com/News/Product_FAQ/147.html)  
57. LM2500 & LM2500XPRESS Gas Turbines | GE Vernova, accessed October 30, 2025, [https://www.gevernova.com/gas-power/products/gas-turbines/lm2500](https://www.gevernova.com/gas-power/products/gas-turbines/lm2500)  
58. LM2500 Gas Turbine, accessed October 30, 2025, [https://mscn7training.com/wp-content/uploads/2021/01/MSC01A\_1211\_B5\_LM2500-Gas-Turbine\_-r5b\_rg.pdf](https://mscn7training.com/wp-content/uploads/2021/01/MSC01A_1211_B5_LM2500-Gas-Turbine_-r5b_rg.pdf)  
59. GER-4250 \- GE's LM2500+G4 Aeroderivative Gas Turbine for Marine and Industrial Applications, accessed October 30, 2025, [https://www.gevernova.com/content/dam/gepower-new/global/en\_US/downloads/gas-new-site/resources/reference/ger-4250-ge-lm2500-g4-aero-gas-turbine-marine-industrial-applications.pdf](https://www.gevernova.com/content/dam/gepower-new/global/en_US/downloads/gas-new-site/resources/reference/ger-4250-ge-lm2500-g4-aero-gas-turbine-marine-industrial-applications.pdf)  
60. LM2500+G4 Marine Gas Turbine \- GE Aerospace, accessed October 30, 2025, [https://www.geaerospace.com/sites/default/files/datasheet-lm2500plusg4.pdf](https://www.geaerospace.com/sites/default/files/datasheet-lm2500plusg4.pdf)  
61. GE Energy LM2500+ G4 Operation and Maintenance Manual: Fuel System Description | PDF | Turbocharger | Valve \- Scribd, accessed October 30, 2025, [https://www.scribd.com/document/481126427/lmx2g4-spd07](https://www.scribd.com/document/481126427/lmx2g4-spd07)  
62. GE Energy LM2500+ G4 Operation and Maintenance Manual: Generator Lube Oil System Description | PDF | Pump \- Scribd, accessed October 30, 2025, [https://www.scribd.com/document/481126431/lmx2g4-spd05](https://www.scribd.com/document/481126431/lmx2g4-spd05)  
63. INFORMATION ABOUT THE LM2500/PGT25 GAS TURBINE TRAINING COURSE BASED ON ALL LM2500 MODELS (INCLUDING \+,+G4, SAC AND DLE) Week 16, accessed October 30, 2025, [https://vbr-turbinepartners.com/wp-content/uploads/2023/03/Training-course-LM2500-Elst-42608777-April-2023.pdf](https://vbr-turbinepartners.com/wp-content/uploads/2023/03/Training-course-LM2500-Elst-42608777-April-2023.pdf)  
64. Sailors LM2500 Pocket Guide \- WordPress.com, accessed October 30, 2025, [https://gasturbinesystems.files.wordpress.com/2018/06/lm2500-pocketguide.pdf](https://gasturbinesystems.files.wordpress.com/2018/06/lm2500-pocketguide.pdf)  
65. Manual LM2500 | PDF \- Scribd, accessed October 30, 2025, [https://www.scribd.com/document/432021422/Manual-LM2500](https://www.scribd.com/document/432021422/Manual-LM2500)  
66. LM2500 Maintenance & Troubleshooting | PDF | N Ox | Combustion \- Scribd, accessed October 30, 2025, [https://www.scribd.com/document/361782869/LM2500-Maintenance-Troubleshooting](https://www.scribd.com/document/361782869/LM2500-Maintenance-Troubleshooting)  
67. Maximum Acceptable Step load \- LM2500 GTG | Automation & Control Engineering Forum, accessed October 30, 2025, [https://control.com/forums/threads/maximum-acceptable-step-load-lm2500-gtg.53316/](https://control.com/forums/threads/maximum-acceptable-step-load-lm2500-gtg.53316/)  
68. LM2500 GE Gas Turbine Vibration Sensors issues (Proximitor) \- Control.com, accessed October 30, 2025, [https://control.com/forums/threads/lm2500-ge-gas-turbine-vibration-sensors-issues-proximitor.51156/](https://control.com/forums/threads/lm2500-ge-gas-turbine-vibration-sensors-issues-proximitor.51156/)  
69. LM2500 \- VBR Turbine Partners, accessed October 30, 2025, [https://vbr-turbinepartners.com/lm2500/](https://vbr-turbinepartners.com/lm2500/)  
70. Spare Parts List For LM Gas Turbines Series | PDF | Propulsion \- Scribd, accessed October 30, 2025, [https://www.scribd.com/document/550613373/TurbineSpareParts-May15](https://www.scribd.com/document/550613373/TurbineSpareParts-May15)