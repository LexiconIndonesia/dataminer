# Product Requirements Document (PRD)
## Intelligent Document Mining Service (Dataminer)

**Version:** 2.0
**Author:** System Architecture Team
**Date:** 2024
**Status:** Multi-Source Support

---

## 1. Executive Summary

### 1.1 Project Overview

Build a production-grade, multi-source document mining service capable of extracting structured data from various legal document sources across multiple countries and languages. The system supports configurable extraction pipelines tailored to each document source's unique structure, language, and legal system.

### 1.2 Key Objectives

- Support 6 document sources with distinct configurations (2 court judgments + 1 regulations + 3 watchlists/databases)
- Extract source-specific fields (65+ for Indonesian SC, 40+ for Singapore SC, 30+ for regulations and blacklists)
- Process 20-50 documents daily across all sources
- Dynamic per-source configuration without code changes
- Multi-language support (Indonesian, English, Malay)
- Maintain extraction cost under $5 per document
- Source-specific validation rules and confidence thresholds
- Automatic source detection and classification
- Cross-source entity matching and deduplication
- Support reprocessing with different configurations

### 1.3 Document Sources Roadmap

| Source ID | Source Name | Country | Language | Document Type | Fields | Priority |
|-----------|------------|---------|----------|---------------|--------|----------|
| ID_SC | Indonesian Supreme Court | Indonesia | Indonesian | Criminal/Civil Judgment | 65+ | Phase 1 |
| ID_LKPP | LKPP Blacklist | Indonesia | Indonesian | Procurement Blacklist | 30+ | Phase 1 |
| SG_SC | Singapore Supreme Court | Singapore | English | Common Law Judgment | 40+ | Phase 1 |
| ID_REG | Indonesian Regulations | Indonesia | Indonesian | Laws/Regulations | 30+ | Phase 2 |
| MY_PR | Malaysia Pesalah Rasuah | Malaysia | Malay/English | Corruption Offenders Database | 25+ | Phase 2 |
| OS | Open Sanction | International | English | Sanctions/Watchlist Database | 35+ | Phase 2 |

### 1.4 Constraints

- **Budget**: Maximum $5 per document including all retries
- **Infrastructure**: Dedicated VPS (dataminer-1) in existing Dokploy setup
- **LLM**: Gemini via Vertex AI (GCP hosted)
- **Languages**: Multi-language support with automatic detection
- **Volume**: 20-50 documents per day across all sources
- **Accuracy Target**: >85% for critical fields, >75% for standard fields

---

## 2. System Architecture

### 2.1 High-Level Architecture

The system implements a source-aware processing pipeline with the following components:

**Document Ingestion Layer**
- Accepts documents from multiple sources (crawler, manual upload, API)
- Performs initial document analysis and language detection
- Routes to appropriate source-specific pipeline

**Source Classification Engine**
- Automatic source detection based on document features
- Language identification and multi-language detection
- Legal system classification (Common Law, Civil Law, Syariah)
- Confidence scoring for source prediction

**Configuration Management System**
- Per-source extraction profiles stored in database
- Dynamic field definitions for each document source
- Source-specific normalization rules
- Language-specific prompt templates
- Real-time configuration updates without restart

**Processing Pipeline (Per Source)**
- PDF extraction with language-appropriate OCR
- Source-specific text normalization
- Intelligent segmentation based on document structure
- Multi-pass LLM extraction with source context
- Field validation with source-specific rules

**Review & Quality System**
- Source-aware confidence thresholds
- Language-appropriate review interface
- Source-specific validation rules
- Cross-source quality metrics

### 2.2 Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Core Language** | Python 3.11+ | Rich NLP/ML ecosystem |
| **PDF Processing** | pdfplumber, PyMuPDF | Multi-language PDF support |
| **OCR Primary** | Tesseract 5.0 | Supports 100+ languages |
| **OCR Fallback** | Google Document AI | Superior for Asian scripts |
| **Language Detection** | langdetect, fasttext | Accurate multi-language detection |
| **Indonesian NLP** | spaCy, Sastrawi | Indonesian text processing |
| **English NLP** | spaCy, NLTK | English legal text processing |
| **Chinese Processing** | jieba, HanLP | Chinese segmentation |
| **Malay Processing** | Malaya | Malay language toolkit |
| **Thai Processing** | PyThaiNLP | Thai text segmentation |
| **LLM Primary** | Gemini 1.5 Pro/Flash | Multi-language capability |
| **LLM Fallback** | GPT-4 | Alternative for specific languages |
| **Translation** | Google Translate API | Cross-language validation |
| **Web Framework** | FastAPI | Async, matches existing stack |
| **Task Queue** | NATS JetStream | Existing infrastructure |
| **Database** | PostgreSQL | Configuration & results storage |
| **Cache** | Redis | Job status, extraction cache |
| **Object Storage** | GCS | PDF and extraction storage |

---

## 3. Functional Requirements

### 3.1 Source Management

**Source Registration**
- Define new document sources with metadata
- Configure source characteristics (language, legal system, typical structure)
- Set source-specific processing defaults
- Define expected document patterns

**Source Configuration**
- Create multiple extraction profiles per source
- Define source-specific field definitions
- Configure extraction methods per field
- Set language-specific prompts
- Define normalization rules per source
- Configure validation rules

**Source Detection**
- Automatic source classification from document content
- Language detection with confidence scores
- Legal system identification
- Fallback mechanisms for uncertain classification

### 3.2 Multi-Language Processing

**Language Support Matrix**

| Language | OCR Support | NLP Support | LLM Support | Sources Using |
|----------|------------|-------------|-------------|---------------|
| Indonesian | Tesseract | spaCy | Gemini | ID_SC, ID_REG, ID_LKPP |
| English | Tesseract | spaCy | Gemini | SG_SC, MY_PR, OS |
| Malay | Tesseract | Malaya | Gemini | MY_PR |

**Language-Specific Features**
- Automatic script detection (Latin, Chinese, Thai, Arabic)
- Right-to-left text support for future Arabic documents
- Mixed-language document handling
- Language-appropriate date and number formatting
- Cultural context awareness in extraction

### 3.3 Source-Specific Field Extraction

**Indonesian Supreme Court (ID_SC)**
- 65+ fields including case details, defendant information, charges, verdict
- Indonesian legal terminology normalization
- Rupiah currency extraction and normalization
- Indonesian date format handling
- Specific sections: DAKWAAN, TUNTUTAN, MENGADILI

**Singapore Supreme Court (SG_SC)**
- 40+ fields including neutral citations, case parties, holdings
- Common law citation extraction
- SGD currency handling
- Paragraph reference extraction
- Specific sections: Coram, Holdings, Grounds

**Indonesian Regulations (ID_REG)**
- 30+ fields including law number, articles, effective date
- Hierarchical article extraction
- Cross-reference handling
- Konsiderans extraction (Menimbang, Mengingat)
- Law type classification (UU, PP, Perpres, Permen)

**Malaysia Pesalah Rasuah (MY_PR)**
- 25+ fields including offender name, IC number, offense details, court case
- Bilingual extraction (Malay/English)
- Malaysian IC/passport number formats
- Court reference extraction
- Company/individual entity type handling

**LKPP Blacklist (ID_LKPP)**
- 30+ fields including company name, NPWP, blacklist reason, period
- Indonesian company registration numbers (NPWP, NIB)
- Blacklist effective dates and duration
- Procurement violation categorization
- Company address and contact normalization

**Open Sanction (OS)**
- 35+ fields including entity name, aliases, nationality, sanction type
- Multi-jurisdiction sanctions handling
- Entity type classification (individual/organization)
- Multiple identifier types (passport, tax ID, registration numbers)
- Sanction program and authority extraction
- Cross-reference to related entities

### 3.4 Configuration Management

**Dynamic Configuration Features**
- Real-time configuration updates without service restart
- Per-source configuration isolation
- Version control for configuration changes
- Configuration validation before activation
- Rollback capability for configurations
- A/B testing support for extraction strategies

**Configurable Elements**
- PDF extraction methods and parameters
- OCR settings and languages
- Text normalization rules
- Segmentation strategies
- LLM models and parameters
- Prompt templates
- Field definitions and extraction methods
- Validation rules and thresholds
- Confidence scoring algorithms
- Review triggers and thresholds

### 3.5 Processing Pipeline

**Stage 1: Document Ingestion**
- Accept documents from multiple sources
- Validate document format and size
- Extract document metadata
- Store in GCS with unique identifier

**Stage 2: Source Classification**
- Sample document pages for analysis
- Detect primary and secondary languages
- Extract source-identifying features
- Classify document source with confidence
- Select appropriate extraction profile

**Stage 3: PDF Processing**
- Apply source-specific PDF extraction
- Fallback to OCR for scanned documents
- Use appropriate OCR languages
- Handle mixed text/image documents
- Extract document structure

**Stage 4: Text Normalization**
- Apply source-specific normalization rules
- Fix OCR errors common to source language
- Standardize legal terminology
- Normalize dates, currencies, numbers
- Handle special characters and formatting

**Stage 5: Intelligent Segmentation**
- Apply source-specific segmentation strategy
- Identify document sections
- Create overlapping segments for context
- Optimize segment size for LLM processing
- Preserve cross-references

**Stage 6: Multi-Pass Extraction**
- Quick scan with fast model
- Detailed extraction for complex fields
- Validation pass for critical fields
- Handle multiple extraction attempts
- Track confidence scores

**Stage 7: Validation & Scoring**
- Apply source-specific validation rules
- Calculate field confidence scores
- Check cross-field consistency
- Flag fields for review
- Generate quality metrics

**Stage 8: Review & Correction**
- Present low-confidence fields for review
- Show alternative extractions
- Allow manual corrections
- Track reviewer decisions
- Update models based on corrections

### 3.6 Quality Assurance

**Confidence Scoring System**
- Source-specific confidence thresholds
- Field category-based requirements (critical, important, standard)
- Multi-factor confidence calculation
- Automatic review triggers
- Confidence trend tracking

**Review Workflow**
- Prioritized review queue
- Source-language appropriate interface
- Side-by-side document and extraction view
- Bulk approval capabilities
- Review time tracking
- Quality metrics per reviewer

**Validation Rules**
- Source-specific format validation
- Legal citation verification
- Date consistency checks
- Monetary amount validation
- Cross-reference validation
- Completeness checks

---

## 4. Data Model

### 4.1 Core Configuration Tables

**document_sources**
- Source identification and metadata
- Country, language, legal system
- Processing defaults
- Document patterns and indicators
- Statistics and metrics

**source_extraction_profiles**
- Multiple profiles per source
- Processing configuration
- Segmentation strategy
- LLM configuration
- Budget allocation
- Version control

**source_field_definitions**
- Field definitions per source
- Extraction methods
- Language-specific settings
- Validation rules
- Confidence thresholds
- Field grouping and categorization

**source_normalization_rules**
- Pattern-based rules per source
- Language-specific corrections
- Priority ordering
- Active/inactive status

**source_prompt_templates**
- Language-appropriate prompts
- Source-specific instructions
- Template versioning
- Performance tracking

### 4.2 Job Processing Tables

**extraction_jobs**
- Source identification (detected and confirmed)
- Language detection results
- Profile selection
- Processing status and stages
- Cost tracking
- Error handling
- Review requirements

**extraction_results**
- Multiple extractions per field
- Confidence scores
- Selected values
- Validation status
- Review history

**document_segments**
- Source-specific segments
- Original and normalized text
- Location information
- Processing costs

### 4.3 Review & Quality Tables

**review_queue**
- Source-aware prioritization
- Language-appropriate grouping
- Assignment management
- Review actions and history

**source_classification_log**
- Classification predictions
- Confidence scores
- Feature extraction
- Manual corrections

**source_extraction_statistics**
- Per-source metrics
- Period-based aggregation
- Field-level statistics
- Quality trends

---

## 5. API Specifications

### 5.1 Source Management

**GET /api/v1/dataminer/sources**
- List all configured document sources
- Filter by country, language, status
- Include statistics and metrics

**GET /api/v1/dataminer/sources/{source_id}**
- Get detailed source configuration
- Include all profiles and fields
- Return processing statistics

**PUT /api/v1/dataminer/sources/{source_id}/config**
- Update source configuration
- Validate before applying
- Support partial updates

**POST /api/v1/dataminer/sources/{source_id}/profiles**
- Create new extraction profile
- Clone from existing profile
- Set as default option

### 5.2 Field Management

**GET /api/v1/dataminer/sources/{source_id}/fields**
- List all fields for source
- Filter by category, status
- Include extraction statistics

**POST /api/v1/dataminer/sources/{source_id}/fields**
- Add new field definition
- Configure extraction method
- Set validation rules

**PUT /api/v1/dataminer/fields/{field_id}**
- Update field configuration
- Modify extraction method
- Adjust confidence thresholds

### 5.3 Job Processing

**POST /api/v1/dataminer/jobs**
- Submit extraction job
- Auto-detect source option
- Override configurations
- Set priority and metadata

**GET /api/v1/dataminer/jobs/{job_id}**
- Get job status and progress
- Include cost tracking
- Return detected source

**GET /api/v1/dataminer/jobs/{job_id}/results**
- Get extraction results
- Include all attempts
- Return confidence scores

**POST /api/v1/dataminer/jobs/{job_id}/reprocess**
- Reprocess with different config
- Target specific fields
- Use different models

### 5.4 Review Management

**GET /api/v1/dataminer/review/queue**
- Get review queue
- Filter by source, language
- Sort by priority

**POST /api/v1/dataminer/review/{review_id}/submit**
- Submit review decisions
- Approve/reject/modify
- Add review notes

**GET /api/v1/dataminer/review/stats**
- Review statistics
- Per-source metrics
- Reviewer performance

### 5.5 Configuration Management

**GET /api/v1/dataminer/config/templates**
- List prompt templates
- Filter by source, language
- Include usage statistics

**POST /api/v1/dataminer/config/templates**
- Create new template
- Set source and language
- Configure variables

**GET /api/v1/dataminer/config/rules**
- List normalization rules
- Filter by source, type
- Include effectiveness metrics

---

## 6. Non-Functional Requirements

### 6.1 Performance Requirements

**Processing Speed**
- Average: <5 minutes per 100-page document
- Peak: Support 10 concurrent jobs
- OCR: <30 seconds per page
- LLM calls: <10 seconds per request
- API response: <500ms (P95)

**Scalability**
- Support 20-50 documents daily (Phase 1)
- Scale to 100+ documents daily (Phase 2)
- Handle documents up to 2000 pages
- Support 6 document sources
- Process 3 languages (Indonesian, English, Malay)

### 6.2 Accuracy Requirements

**Extraction Accuracy by Field Category**
- Critical fields: >85% accuracy
- Important fields: >80% accuracy
- Contextual fields: >75% accuracy
- Standard fields: >70% accuracy

**Source-Specific Targets**
- Indonesian SC (ID_SC): 85% overall accuracy
- Singapore SC (SG_SC): 90% overall accuracy
- Indonesian Regulations (ID_REG): 88% overall accuracy
- Malaysia Pesalah Rasuah (MY_PR): 85% overall accuracy
- LKPP Blacklist (ID_LKPP): 80% overall accuracy
- Open Sanction (OS): 85% overall accuracy

### 6.3 Cost Requirements

**Per Document Costs**
- Average: <$2 per document
- Maximum: <$5 per document
- OCR usage: <20% of documents
- Retry budget: 10% of base cost

**Cost Breakdown Targets**
- LLM calls: 60% of cost
- OCR (when needed): 30% of cost
- Translation: 5% of cost
- Other APIs: 5% of cost

### 6.4 Reliability Requirements

**System Availability**
- Uptime: 99% during business hours
- Graceful degradation for failures
- Automatic retry mechanisms
- Job recovery after crashes

**Data Integrity**
- No data loss during processing
- Transactional consistency
- Audit trail for all changes
- Version control for configurations

### 6.5 Security Requirements

**Access Control**
- Role-based access control
- Source-level permissions
- API authentication
- Audit logging

**Data Protection**
- Encryption at rest (GCS)
- Encryption in transit (TLS)
- PII handling compliance
- Document retention policies

---

## 7. Monitoring & Analytics

### 7.1 Operational Metrics

**System Metrics**
- Job processing rate by source
- Average processing time by source
- Queue depth by priority
- Error rates by stage
- Resource utilization

**Quality Metrics**
- Extraction accuracy by source
- Field confidence distributions
- Review completion rates
- Manual correction rates
- Source classification accuracy

**Cost Metrics**
- Cost per document by source
- LLM token usage
- OCR page counts
- API call volumes
- Budget utilization

### 7.2 Dashboards

**Operations Dashboard**
- Real-time job status
- Queue visualization
- Error alerts
- Resource usage
- Cost tracking

**Quality Dashboard**
- Accuracy trends by source
- Field performance
- Review metrics
- Confidence distributions
- Error analysis

**Source Analytics Dashboard**
- Per-source statistics
- Language distribution
- Document type breakdown
- Processing time trends
- Cost analysis

---

## 8. Implementation Phases

### 8.1 Phase 1: Initial Sources (Months 1-2)

**Deliverables**
- Indonesian Supreme Court support
- LKPP Blacklist support
- Singapore Supreme Court support
- Basic review interface
- Configuration management

**Success Criteria**
- Process 20 documents daily
- 85% accuracy for ID_SC
- 80% accuracy for ID_LKPP
- 90% accuracy for SG_SC
- Review workflow operational

### 8.2 Phase 2: Expansion Sources (Months 3-4)

**Deliverables**
- Indonesian Regulations support
- Malaysia Pesalah Rasuah support
- Open Sanction support
- Advanced review features
- Cross-source entity matching
- API for external integration

**Success Criteria**
- Process 40 documents daily
- 88% accuracy for ID_REG
- 85% accuracy for MY_PR
- 85% accuracy for OS
- Entity deduplication working
- Full API availability

### 8.3 Phase 3: Advanced Features (Months 5-6)

**Deliverables**
- Active learning from corrections
- Cross-source analytics
- Entity relationship mapping
- Automated alerts for matches
- Bulk export capabilities

**Success Criteria**
- Process 50+ documents daily
- All sources >85% accuracy
- Learning improving accuracy
- Cross-source matching operational

---

## 9. Risk Analysis

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Poor OCR quality for Asian scripts | High | Medium | Use Document AI for critical documents |
| Source misclassification | High | Low | Manual override option, confidence thresholds |
| Language model limitations | Medium | Medium | Multiple model fallbacks, human review |
| Configuration complexity | Medium | High | Template library, configuration validation |
| Budget overruns | Medium | Low | Real-time tracking, automatic limits |
| Multi-language complexity | High | Medium | Language-specific pipelines, native speakers for review |
| Legal terminology variations | Medium | High | Expandable terminology database |
| Scaling bottlenecks | Medium | Low | Horizontal scaling design, queue management |

---

## 10. Success Criteria

### 10.1 Functional Success

- [ ] Support for 6 document sources (2 court judgments + 1 regulations + 3 watchlists/databases)
- [ ] Multi-language extraction operational (Indonesian, English, Malay)
- [ ] Dynamic configuration working
- [ ] Review workflow efficient
- [ ] Source auto-detection accurate
- [ ] Cross-source entity matching functional
- [ ] Reprocessing capability available

### 10.2 Performance Success

- [ ] Meeting processing speed targets
- [ ] Achieving accuracy thresholds
- [ ] Staying within cost budgets
- [ ] Handling concurrent loads
- [ ] Scaling to volume requirements

### 10.3 Quality Success

- [ ] Field accuracy meets targets
- [ ] Review completion >95%
- [ ] False positive rate <5%
- [ ] User satisfaction >85%
- [ ] Configuration errors <1%

---

## 11. Future Enhancements

### 11.1 Near-term (6-12 months)

- Additional watchlist sources (UN sanctions, OFAC, EU sanctions)
- Additional ASEAN court systems
- Enhanced entity resolution and matching
- Table extraction capabilities
- Automated source onboarding
- Machine learning model training
- Real-time alerts for new entries

### 11.2 Long-term (12+ months)

- Real-time extraction API
- Streaming document processing
- Cross-jurisdiction entity tracking
- Entity relationship network visualization
- Legal knowledge graph
- Predictive risk scoring
- Automated compliance monitoring

---

## 12. Appendices

### 12.1 Glossary

**Terms**
- **Source**: A specific document origin (e.g., Indonesian Supreme Court)
- **Profile**: Configuration set for processing documents from a source
- **Field**: Specific data point to extract (e.g., case number, defendant name)
- **Segment**: Portion of document identified for processing
- **Confidence Score**: Probability of extraction correctness (0-1)
- **Review Queue**: List of extractions requiring human verification
- **Normalization**: Process of standardizing text format
- **Classification**: Process of identifying document source

### 12.2 Document Sources Reference

**Legal Systems**
- **Civil Law**: Indonesia, Thailand, Philippines (mixed)
- **Common Law**: Singapore, Malaysia, Philippines (mixed)
- **Syariah Law**: Malaysia (parallel system), Indonesia (Aceh)

**Language Families**
- **Austronesian**: Indonesian, Malay, Filipino
- **Sino-Tibetan**: Chinese (Mandarin, Hokkien)
- **Tai-Kadai**: Thai
- **Indo-European**: English

---

**Document Version**: 2.0
**Last Updated**: 2024
**Status**: Ready for Implementation
**Approval**: Pending
