# Product Requirements Document: Indonesian Supreme Court (ID_SC)

**Version:** 1.0
**Source ID:** ID_SC
**Author:** System Architecture Team
**Date:** 2024
**Status:** Phase 1 - Ready for Implementation

---

## 1. Executive Summary

### 1.1 Overview

The Indonesian Supreme Court (Mahkamah Agung) document mining module is the primary Phase 1 source for the Dataminer service. This module extracts structured data from Indonesian criminal and civil court judgments published on the Supreme Court's website (https://putusan3.mahkamahagung.go.id/).

### 1.2 Document Characteristics

| Attribute | Value |
|-----------|-------|
| **Source Type** | Court Judgments |
| **Legal System** | Civil Law (Indonesian) |
| **Primary Language** | Indonesian (Bahasa Indonesia) |
| **Document Format** | PDF (mostly searchable, some scanned) |
| **Typical Length** | 10-200 pages (corruption cases typically 50-150 pages) |
| **Update Frequency** | Daily |
| **Volume Target** | 10-20 documents daily |
| **Field Count** | **72 fields** (optimized for corruption cases) |

### 1.3 Key Objectives

- Extract **72 structured fields** from Indonesian corruption case judgments (Tindak Pidana Korupsi)
- Focus on **corruption cases** with detailed financial tracking:
  - State losses (Kerugian Negara)
  - Restitution payments (Uang Pengganti)
  - Recovered funds (Pengembalian Kerugian Negara)
  - Corruption proceeds (Uang Korupsi yang Diperoleh)
- Handle Indonesian legal terminology and court document formatting
- Process Rupiah currency values (often in billions) with high accuracy
- Extract hierarchical charge structures (Dakwaan Primair/Subsidair)
- Compare prosecutor demands (Tuntutan) vs. actual verdict (Amar)
- Extract mitigating and aggravating factors (5+ factors each)
- Identify all parties: judges, prosecutors, defense lawyers, auditors (BPKP/BPK)
- Maintain >90% accuracy for critical fields (identifiers, financial amounts, sentences)
- Keep processing cost <$2 per document average

### 1.4 Constraints

- **Language**: Indonesian only (no mixed language in most documents)
- **OCR Requirement**: ~15-20% of documents are scanned
- **Legal System**: Civil law structure (different from common law)
- **Document Quality**: Varies significantly by court level
- **Terminology**: Highly standardized Indonesian legal terms

---

## 2. Document Structure Analysis

### 2.1 Standard Document Sections

Indonesian Supreme Court judgments follow a standardized structure:

#### **Header Section**
```
PUTUSAN
Nomor: {case_number}
DEMI KEADILAN BERDASARKAN KETUHANAN YANG MAHA ESA
```
Contains:
- Case number (format: Number/Case Type/Court/Year)
- Court level (PN, PT, MA)
- Decision date
- Case type (Pidana/Perdata)

#### **Identity Section (IDENTITAS)**
```
Mahkamah Agung tersebut;
Membaca surat-surat yang bersangkutan;
```
Contains:
- Defendant/plaintiff information
- ID numbers (NIK/KTP)
- Birth dates and places
- Addresses
- Occupations

#### **Case Background (DUDUK PERKARA)**
Contains:
- Arrest date and location
- Initial charges
- Investigation details
- Previous court decisions

#### **Charges Section (DAKWAAN)**
For criminal cases:
- Primary charge (Dakwaan Primair)
- Alternative charges (Dakwaan Subsidair, Lebih Subsidair)
- Legal basis (articles and laws)
- Elements of crime (Unsur-unsur)

#### **Evidence Section (BARANG BUKTI)**
Lists:
- Physical evidence
- Documentary evidence
- Witness testimonies
- Expert testimonies

#### **Prosecution Demands (TUNTUTAN JAKSA PENUNTUT UMUM)**
Contains:
- Prosecutor's sentence demand
- Legal reasoning
- Proposed penalties

#### **Court Considerations (PERTIMBANGAN HUKUM)**
Contains:
- Legal analysis
- Facts assessment
- Law application
- Mitigating/aggravating factors

#### **Verdict Section (MENGADILI/MEMUTUSKAN)**
```
MENGADILI:
1. Menyatakan Terdakwa [name] telah terbukti...
2. Menjatuhkan pidana...
3. Menetapkan barang bukti...
```
Contains:
- Guilt determination
- Sentence (imprisonment, fines, etc.)
- Evidence disposition
- Legal costs

#### **Panel Information (MAJELIS HAKIM)**
Contains:
- Presiding judge
- Panel judges
- Clerk (Panitera)

### 2.2 Document Variations

**By Court Level:**
- **PN (Pengadilan Negeri)**: First instance, more detailed
- **PT (Pengadilan Tinggi)**: Appeal, references to lower court
- **MA (Mahkamah Agung)**: Cassation, shorter, focused on legal questions

**By Case Type:**
- **Pidana (Criminal)**: Structured with Dakwaan, more standardized
- **Perdata (Civil)**: More varied structure, focuses on claims and counterclaims

**By Quality:**
- **High Quality**: Recent documents, searchable PDF, clear structure
- **Medium Quality**: Older documents, some OCR errors, readable
- **Low Quality**: Scanned, poor OCR quality, requires Document AI

---

## 3. Field Definitions

### 3.1 Field Categories

Based on actual requirements, the ID_SC extraction involves **77 fields** organized into the following categories:

| Category | Count | Accuracy Target | Review Trigger | Description |
|----------|-------|-----------------|----------------|-------------|
| Document & Court Information | 9 | >90% | <90% confidence | Case registration, court details, dates |
| Defendant Information | 10 | >90% | <85% confidence | Personal details, demographics |
| Pre-Trial Detention | 5 | >85% | <85% confidence | Detention dates, duration, type |
| Legal Representatives | 4 | >85% | <80% confidence | Lawyers, prosecutors, judges, clerk |
| Charge Information (Dakwaan) | 9 | >88% | <85% confidence | Charges, legal articles, crime details |
| Prosecution Demands (Tuntutan) | 7 | >85% | <85% confidence | Prosecutor's sentence demands |
| Verdict Information (Amar) | 16 | >92% | <90% confidence | Final verdict, sentences, penalties |
| Financial & Corruption Details | 9 | >90% | <88% confidence | State losses, restitution, corruption money |
| Mitigating & Aggravating Factors | 10 | >75% | <70% confidence | Court's reasoning for sentencing |

**Total: 77 fields** (+2 including derived fields)

**Note:** This field structure is optimized for **corruption cases (Tindak Pidana Korupsi)** which include detailed financial tracking, state losses, and restitution payments. For other case types (narcotics, general criminal), some financial fields may be null.

### 3.2 Document & Court Information (9 fields)

| No | Field ID (Parameter Name) | Indonesian Name | Type | Example | Extraction Source |
|----|---------------------------|----------------|------|---------|-------------------|
| 1 | `sequence_number` | NO | Integer | 1 | Sequential numbering |
| 2 | `case_registration_number` | REGISTER PUTUSAN | String | "123/Pid.Sus-TPK/2023/PN Jkt.Pst" | Header section - Regex + LLM |
| 3 | `verdict_number` | NOMOR PUTUSAN | String | "123/Pid.Sus-TPK/2023/PN Jkt.Pst" | Header - same as case_registration_number |
| 4 | `verdict_date` | TANGGAL PUTUSAN | Date | "2023-10-15" | Header - Date parsing |
| 5 | `verdict_year` | TAHUN PUTUSAN | Integer | 2023 | Extracted from verdict_number |
| 6 | `verdict_day_of_week` | HARI PUTUSAN | String | "Rabu" | From verdict_date |
| 7 | `court_region` | DAERAH PENGADILAN | String | "Jakarta Pusat" | From case number/court name |
| 8 | `province` | PROVINSI | String | "DKI Jakarta" | Derived from court_region |
| 9 | `verdict_ruling_date` | TANGGAL AMAR | Date | "2023-10-15" | MENGADILI section (usually same as verdict_date) |
| - | `verdict_ruling_day_of_week` | HARI AMAR | String | "Rabu" | Derived from verdict_ruling_date |

**Validation Rules:**
- Case registration number format: `\d+/Pid\.(Sus-)?TPK/\d{4}/(PN|PT|MA)[\s\w.]+`
- Verdict year must be 1945-present
- Day of week must be Indonesian day name (Senin-Minggu)
- Verdict ruling date usually equals verdict date

### 3.3 Defendant Information (10 fields)

| No | Field ID (Parameter Name) | Indonesian Name | Type | Example | Extraction Source |
|----|---------------------------|----------------|------|---------|-------------------|
| 10 | `defendant_name` | NAMA TERDAKWA | String | "AHMAD BIN HASAN" | IDENTITAS section - LLM |
| 11 | `defendant_birth_place` | TEMPAT LAHIR | String | "Jakarta" | IDENTITAS - LLM |
| 12 | `defendant_birth_date` | TANGGAL LAHIR | Date | "1985-06-15" | IDENTITAS - Date parsing |
| 13 | `defendant_age` | UMUR | Integer | 38 | IDENTITAS - Direct or calculated |
| 14 | `defendant_gender` | JENIS KELAMIN | Enum | "Laki-laki"/"Perempuan" | IDENTITAS - LLM |
| 15 | `defendant_nationality` | KEWARGANEGARAAN | String | "Indonesia" | IDENTITAS - LLM |
| 16 | `defendant_address` | ALAMAT | String | "Jl. Sudirman No. 10, Jakarta" | IDENTITAS - LLM |
| 17 | `defendant_religion` | AGAMA | String | "Islam" | IDENTITAS - LLM |
| 18 | `defendant_occupation` | PEKERJAAN | String | "Pegawai Negeri Sipil" | IDENTITAS - LLM |
| 19 | `defendant_education` | PENDIDIKAN | String | "S1" | IDENTITAS - LLM |

**Validation Rules:**
- Birth date must result in age = verdict_year - birth_year (±1)
- Gender must be "Laki-laki" or "Perempuan"
- Age must be 17-100 at time of trial
- Nationality typically "Indonesia" or "WNA"

### 3.4 Pre-Trial Detention (5 fields)

| No | Field ID (Parameter Name) | Indonesian Name | Type | Example | Extraction Source |
|----|---------------------------|----------------|------|---------|-------------------|
| 20 | `detention_start_date` | TANGGAL MULAI PENAHANAN | Date | "2023-04-15" | IDENTITAS/DUDUK PERKARA - LLM |
| 21 | `detention_end_date` | TANGGAL AKHIR PENAHANAN | Date | "2023-10-15" | IDENTITAS/AMAR - LLM + Validation |
| 22 | `detention_duration_days` | MASA PENAHANAN (HARI) | Integer | 183 | Calculated |
| 23 | `detention_type` | JENIS PENAHANAN | String | "Rutan"/"Lapas"/"Tahanan Rumah" | IDENTITAS - LLM |
| 24 | `detention_deducted` | PENAHANAN DIKURANGKAN | Boolean | true | MENGADILI - LLM |

**Validation Rules:**
- **CRITICAL**: If `detention_end_date` > `verdict_date`, then `detention_end_date` = `verdict_date`
  - Rationale: Detention cannot extend beyond the verdict date
  - Applied automatically during post-processing
- Detention start date must be ≤ detention end date
- Detention duration = (detention_end_date - detention_start_date) in days
- Detention start should be ≤ verdict date
- If detention_deducted = true, must be mentioned in MENGADILI section
- Detention type typically: "Rutan" (Rumah Tahanan), "Lapas" (Lembaga Pemasyarakatan), "Tahanan Rumah", "Tahanan Kota"

### 3.5 Legal Representatives (4 fields)

| No | Field ID (Parameter Name) | Indonesian Name | Type | Example | Extraction Source |
|----|---------------------------|----------------|------|---------|-------------------|
| 25 | `defense_lawyer_name` | NAMA PH (Penasehat Hukum) | Text (multi) | "Budiman, S.H.; Siti, S.H., M.H." | IDENTITAS/header - LLM |
| 26 | `defense_lawyer_office_address` | KANTOR DAN ALAMAT PH | String | "Kantor Hukum ABC, Jl. Thamrin" | IDENTITAS - LLM |
| 27 | `prosecutor_name` | NAMA JAKSA | Text (multi) | "Andi Wijaya, S.H.; Rini Susanti, S.H." | TUNTUTAN/footer - LLM |
| 28 | `court_clerk_name` | NAMA PANITERA | String | "Rudi Hartono" | Footer/signature - LLM |
| - | `judge_name` | NAMA HAKIM | Text (multi) | "Bambang, S.H. (Ketua); Siti, S.H.; Ahmad, S.H." | MAJELIS HAKIM - LLM |

**Validation Rules:**
- Names should include professional titles (S.H., M.H., etc.)
- Defense lawyer can be null if defendant has no lawyer
- Prosecutor and court clerk are required fields
- **Multi-value fields**: Use semicolon (`;`) separator for multiple lawyers/prosecutors/judges
  - Example: "Name1, S.H.; Name2, S.H., M.H."
  - Preserve commas within individual names
  - Store as single TEXT field in database

### 3.5 Charge Information - Dakwaan (9 fields)

| No | Field ID (Parameter Name) | Indonesian Name | Type | Example | Extraction Source |
|----|---------------------------|----------------|------|---------|-------------------|
| 24 | `charge_chronology` | KRONOLOGIS DAKWAAN | Text | Full chronology | DAKWAAN section - LLM |
| 25 | `crime_location` | LOCUS DELICTI | String | "Kantor Dinas XYZ, Jakarta" | DAKWAAN - LLM |
| 26 | `crime_time_period` | TEMPUS DELICTI | String/DateRange | "Januari 2020 - Maret 2021" | DAKWAAN - LLM |
| 27 | `state_loss_charged` | KERUGIAN NEGARA (DAKWAAN) | Integer | 5000000000 | DAKWAAN - Currency parsing |
| 28 | `article_charged_first` | PASAL MUNCUL PERTAMA | String | "Pasal 2 ayat (1)" | DAKWAAN - Regex + LLM |
| 29 | `article_charged_second` | PASAL MUNCUL KEDUA | String | "Pasal 3" | DAKWAAN - Regex + LLM |
| 30 | `article_charged_third` | PASAL MUNCUL KETIGA | String | "Pasal 18" | DAKWAAN - Regex + LLM |
| 31 | `article_charged_fourth` | PASAL MUNCUL KE-EMPAT | String | null | DAKWAAN - Regex + LLM |
| 32 | `charge_structure_type` | BENTUK DAKWAAN | Enum | "Alternatif"/"Subsidair"/"Kumulatif" | DAKWAAN - LLM classification |
| 33 | `defense_objection` | EKSEPSI DAKWAAN | Text | Defense objection details | Before DAKWAAN - LLM |

**Validation Rules:**
- Article format: "Pasal \d+( ayat \(\d+\))?" jo. "UU No. \d+ Tahun \d{4}"
- State loss must be non-negative integer (Rupiah)
- Charge structure must be one of: "Tunggal", "Alternatif", "Subsidair", "Kumulatif", "Kombinasi"
- Crime time period can be date range or approximate period

### 3.6 Prosecution Demands - Tuntutan (7 fields)

| No | Field ID (Parameter Name) | Indonesian Name | Type | Example | Extraction Source |
|----|---------------------------|----------------|------|---------|-------------------|
| 34 | `prosecution_demand_date` | TUNTUTAN (TANGGAL) | Date | "2023-09-20" | TUNTUTAN section - Date parsing |
| 35 | `prosecution_article` | PASAL TUNTUTAN | String | "Pasal 2 ayat (1) jo. Pasal 18" | TUNTUTAN - Regex + LLM |
| 36 | `prosecution_demand_content` | ISI TUNTUTAN | Text | Full prosecution demand text | TUNTUTAN - LLM |
| 37 | `prosecution_prison_demand` | TUNTUTAN PIDANA BADAN TERDAKWA | String | "6 tahun penjara" | TUNTUTAN - LLM |
| 38 | `prosecution_prison_type` | KURUNGAN/PENJARA (Tuntutan) | Enum | "Penjara"/"Kurungan" | TUNTUTAN - LLM |
| 39 | `prosecution_prison_months` | WAKTU (BULAN) - Tuntutan | Integer | 72 | Calculated from prosecution_prison_demand |
| 40 | `prosecution_fine_demand` | TUNTUTAN DENDA TERDAKWA | Integer | 500000000 | TUNTUTAN - Currency parsing |
| 41 | `prosecution_restitution_demand` | TUNTUTAN UANG PENGGANTI | Integer | 3000000000 | TUNTUTAN - Currency parsing |
| 42 | `prosecution_restitution_alternative` | PIDANA PENGGANTI UANG PENGGANTI | String | "1 tahun penjara" | TUNTUTAN - LLM |
| 43 | `prosecution_restitution_alternative_months` | DURASI (Tuntutan Uang Pengganti) | Integer | 12 | Calculated |

**Validation Rules:**
- Demand date must be before verdict_date
- Prison duration must be positive
- Article should reference corruption law (UU Tipikor)
- Restitution and alternative prison must both exist or both be null

### 3.7 Verdict Information - Amar Putusan (16 fields)

| No | Field ID (Parameter Name) | Indonesian Name | Type | Example | Extraction Source |
|----|---------------------------|----------------|------|---------|-------------------|
| 44 | `legal_facts` | FAKTA HUKUM | Text | Court's legal findings summary | PERTIMBANGAN HUKUM - LLM |
| 45 | `verdict_article` | PASAL AMAR | String | "Pasal 2 ayat (1)" | MENGADILI section - Regex + LLM |
| 46 | `verdict_article_conjunction_1` | Jo. (I) | String | "Pasal 18 UU Tipikor" | MENGADILI - Regex + LLM |
| 47 | `verdict_article_conjunction_2` | Jo. (II) | String | "UU No. 31 Tahun 1999" | MENGADILI - Regex + LLM |
| 48 | `verdict_content` | ISI AMAR | Text | Full verdict text | MENGADILI - LLM |
| 49 | `verdict_prison_sentence` | PIDANA BADAN AMAR | String | "4 tahun penjara" | MENGADILI - LLM |
| 50 | `verdict_prison_type` | KURUNGAN/PENJARA (Amar) | Enum | "Penjara"/"Kurungan" | MENGADILI - LLM |
| 51 | `verdict_prison_total_months` | TOTAL BULAN | Integer | 48 | Calculated |
| 52 | `verdict_fine_amount` | PIDANA DENDA AMAR | Integer | 200000000 | MENGADILI - Currency parsing |
| 53 | `verdict_restitution_amount` | UANG PENGGANTI | Integer | 2500000000 | MENGADILI - Currency parsing |
| 54 | `verdict_restitution_alternative` | KURUNGAN/PENJARA PENGGANTI UANG PENGGANTI | String | "6 bulan penjara" | MENGADILI - LLM |
| 55 | `verdict_restitution_alternative_months` | DURASI (BULAN) - Pengganti | Integer | 6 | Calculated |
| 56 | `state_loss_recovered` | PENGEMBALIAN KERUGIAN NEGARA | Integer | 500000000 | MENGADILI/PERTIMBANGAN - LLM |
| 57 | `corruption_proceeds` | UANG KORUPSI YANG DIPEROLEH | Integer | 3000000000 | PERTIMBANGAN - LLM |
| 58 | `remaining_restitution` | SISA UANG PENGGANTI YANG HARUS DIBAYARKAN | Integer | 2000000000 | Calculated: verdict_restitution_amount - state_loss_recovered |
| 59 | `state_loss_verdict` | KERUGIANAMAR | Integer | 2500000000 | PERTIMBANGAN/AMAR - LLM |
| 60 | `state_loss_auditor` | PEMERIKSA KERUGIAN NEGARA | String | "BPKP"/"BPK"/"Inspektorat" | PERTIMBANGAN - LLM |

**Validation Rules:**
- Verdict article must be one of the charged articles
- Total months = years * 12 + months from verdict_prison_sentence
- Remaining restitution = verdict_restitution_amount - state_loss_recovered
- State loss verdict should be ≤ state_loss_charged
- All currency fields in Rupiah (integer)

### 3.8 Mitigating & Aggravating Factors (10+ fields)

| No | Field ID (Parameter Name) | Indonesian Name | Type | Example | Extraction Source |
|----|---------------------------|----------------|------|---------|-------------------|
| 61 | `aggravating_factor_1` | ALASAN MEMBERATKAN I | String | "Perbuatan terdakwa merugikan negara" | PERTIMBANGAN - LLM |
| 62 | `aggravating_factor_2` | ALASAN MEMBERATKAN II | String | "Tidak mendukung program pemerintah" | PERTIMBANGAN - LLM |
| 63 | `aggravating_factor_3` | ALASAN MEMBERATKAN III | String | null | PERTIMBANGAN - LLM |
| 64 | `aggravating_factor_4` | ALASAN MEMBERATKAN IV | String | null | PERTIMBANGAN - LLM |
| 65 | `aggravating_factor_5` | ALASAN MEMBERATKAN V | String | null | PERTIMBANGAN - LLM |
| 66 | `mitigating_factor_1` | ALASAN MERINGANKAN I | String | "Terdakwa bersikap sopan" | PERTIMBANGAN - LLM |
| 67 | `mitigating_factor_2` | ALASAN MERINGANKAN II | String | "Terdakwa belum pernah dihukum" | PERTIMBANGAN - LLM |
| 68 | `mitigating_factor_3` | ALASAN MERINGANKAN III | String | "Terdakwa menyesali perbuatannya" | PERTIMBANGAN - LLM |
| 69 | `mitigating_factor_4` | ALASAN MERINGANKAN IV | String | "Terdakwa memiliki tanggungan keluarga" | PERTIMBANGAN - LLM |
| 70 | `mitigating_factor_5` | ALASAN MERINGANKAN V | String | null | PERTIMBANGAN - LLM |
| 71 | `mitigating_factor_6` | ALASAN MERINGANKAN VI | String | null | PERTIMBANGAN - LLM |
| 72 | `mitigating_factor_7` | ALASAN MERINGANKAN VII | String | null | PERTIMBANGAN - LLM |

**Validation Rules:**
- Fields can be null if not mentioned in verdict
- Extract in order as they appear in PERTIMBANGAN HUKUM section
- Typically 2-3 aggravating factors and 3-5 mitigating factors
- Extract as direct quotes from document where possible

### 3.9 Field Summary

**Total Fields: 77** (not including derived fields like verdict_day_of_week, verdict_ruling_day_of_week)

**Required Fields** (must extract with high confidence):
- Document info: `case_registration_number`, `verdict_number`, `verdict_date`
- Defendant: `defendant_name`, `defendant_birth_date`
- Verdict: `verdict_article`, `verdict_content`, `verdict_prison_total_months`

**Conditional Fields** (required for corruption cases):
- `state_loss_charged`
- `verdict_restitution_amount`
- `state_loss_recovered`
- `state_loss_auditor`

**Optional Fields** (may be null):
- Detention: `detention_start_date`, `detention_end_date`, `detention_type` (if defendant was not detained)
- `defense_lawyer_name`, `defense_lawyer_office_address` (if no defense lawyer)
- `defense_objection` (if no defense objection)
- `article_charged_third`, `article_charged_fourth`
- `aggravating_factor_3` through `aggravating_factor_5`
- `mitigating_factor_5` through `mitigating_factor_7`

**Critical Validation Rules:**
- **Detention Date Cap**: `detention_end_date` cannot exceed `verdict_date`. If extracted value > verdict_date, automatically set `detention_end_date = verdict_date`
- **Date Sequence**: `detention_start_date` ≤ `detention_end_date` ≤ `verdict_date`
- **Duration Calculation**: `detention_duration_days = (detention_end_date - detention_start_date)`

**Multi-Value Fields:**

Some fields can contain multiple values. Store as **single TEXT field** with **semicolon (`;`) separator**:

| Field | Can Have Multiple Values | Example | Storage Format |
|-------|-------------------------|---------|----------------|
| `defense_lawyer_name` | ✅ Yes | "Ahmad Budiman, S.H.; Siti Rahma, S.H., M.H." | Single TEXT with `;` separator |
| `prosecutor_name` | ✅ Yes | "Andi Wijaya, S.H.; Rini Susanti, S.H." | Single TEXT with `;` separator |
| `judge_name` | ✅ Yes (panel) | "Dr. Bambang, S.H. (Ketua); Siti, S.H.; Ahmad, S.H." | Single TEXT with `;` separator |
| `aggravating_factor_1-5` | ❌ No | One value per field | Separate fields |
| `mitigating_factor_1-7` | ❌ No | One value per field | Separate fields |

**Separator Rules:**
- Use **semicolon (`;`)** as primary separator for multiple values
- Preserve commas within names (e.g., "S.H., M.H." stays intact)
- Trim whitespace around each value after splitting
- Example parsing: `"Name1, S.H.; Name2, S.H., M.H.".split(';').map(s => s.trim())`

**Database Storage:**
- All multi-value fields stored as `TEXT` type
- No array types used for compatibility
- Application layer handles splitting/joining

---

## 4. Implementation Architecture

### 4.1 Processing Pipeline

#### Stage 1: Document Preprocessing
```python
Input: PDF file from ID_SC source
Output: Normalized text + metadata

Steps:
1. PDF Analysis
   - Page count detection
   - Text extraction attempt with pdfplumber
   - Quality assessment (searchable vs scanned)

2. OCR Decision
   - If text extraction success rate < 80%, use OCR
   - Use Tesseract with Indonesian language pack (ind)
   - Fallback to Document AI for low-quality scans

3. Initial Metadata Extraction
   - Extract case number from first page
   - Identify court level from case number
   - Detect document structure markers
```

#### Stage 2: Text Normalization
```python
Normalization Rules for Indonesian Legal Documents:

1. OCR Error Correction
   - Common mistakes: 'l' vs 'I', 'O' vs '0'
   - Indonesian-specific: 'di' vs 'dI', 'yang' vs 'yank'

2. Legal Term Standardization
   - "Terdakwa" capitalization
   - "Pasal" and "Ayat" formatting
   - Currency notation: "Rp." standardization

3. Date Normalization
   - Convert: "Lima Belas Oktober Dua Ribu Dua Puluh Tiga"
   - To: "15 Oktober 2023"
   - Then to ISO: "2023-10-15"

4. Name Normalization
   - Uppercase to title case
   - "Bin" and "Binti" handling
   - Remove excessive whitespace

5. Legal Citation Formatting
   - Standardize: "UU No. 35 Tahun 2009"
   - Article refs: "Pasal 114 ayat (2)"
```

#### Stage 3: Document Segmentation
```python
Segmentation Strategy:

1. Section Identification (Regex-based)
   - Header: Start to "DUDUK PERKARA"
   - Identity: "Membaca surat" to "DUDUK PERKARA"
   - Background: "DUDUK PERKARA" to "DAKWAAN"
   - Charges: "DAKWAAN" to "BARANG BUKTI"
   - Evidence: "BARANG BUKTI" to "TUNTUTAN"
   - Prosecution: "TUNTUTAN" to "PERTIMBANGAN"
   - Considerations: "PERTIMBANGAN" to "MENGADILI"
   - Verdict: "MENGADILI" to end

2. Segment Size Optimization
   - Target: 2000-4000 tokens per segment
   - Overlap: 200 tokens between segments
   - Preserve section boundaries

3. Cross-reference Preservation
   - Maintain references to case numbers
   - Link evidence mentions across sections
   - Preserve legal article citations
```

#### Stage 4: Multi-Pass Extraction
```python
Pass 1: Quick Scan (Gemini Flash)
- Extract critical identifiers
- Identify case type and structure
- Estimate document complexity
- Cost: ~$0.10 per document

Pass 2: Detailed Extraction (Gemini Pro)
- Extract all 65+ fields
- Process each section with targeted prompts
- Extract hierarchical data (charges, evidence)
- Cost: ~$0.80 per document

Pass 3: Validation Pass (Gemini Flash)
- Verify critical field consistency
- Cross-check dates, names, numbers
- Validate legal citations
- Cost: ~$0.10 per document

Conditional Pass 4: Deep Dive (if needed)
- For low confidence fields
- Complex hierarchical structures
- Ambiguous legal reasoning
- Cost: ~$0.30 per document (10-20% of docs)
```

### 4.2 Extraction Prompts

#### Prompt Template Structure
```python
SYSTEM_PROMPT = """
You are a legal document extraction specialist for Indonesian Supreme Court judgments.
You understand Indonesian legal terminology, document structure, and citation formats.

Your task is to extract structured data from court judgment sections with high accuracy.

Guidelines:
- Extract exactly as written, preserve original spelling
- For dates, provide in ISO format (YYYY-MM-DD)
- For currency, extract numeric value only (no "Rp." prefix)
- For names, preserve capitalization from document
- If information not found, return null
- If unsure, provide confidence score
"""

SECTION_PROMPTS = {
    "header": """
    Extract the following fields from this court judgment header:
    - case_number: Full case number including all parts
    - court_level: PN, PT, or MA
    - court_name: Full court name
    - court_location: Location/jurisdiction
    - decision_date: Date in YYYY-MM-DD format
    - case_type_code: Case type code (e.g., Pid.Sus, Pdt.G)

    Respond in JSON format with confidence scores for each field.
    """,

    "defendant": """
    Extract defendant/party information:
    - defendant_name: Full legal name
    - defendant_alias: Any aliases or nicknames (array)
    - defendant_nik: NIK/KTP number (16 digits)
    - defendant_birth_place: Tempat lahir
    - defendant_birth_date: Tanggal lahir in YYYY-MM-DD
    - defendant_gender: LAKI-LAKI or PEREMPUAN
    - defendant_occupation: Pekerjaan
    - defendant_address: Full address
    - defendant_education: Pendidikan
    - defendant_religion: Agama
    - defendant_marital_status: Status perkawinan

    Respond in JSON format.
    """,

    "charges": """
    Extract charge information from DAKWAAN section:

    For each charge level (Primair, Subsidair, Lebih Subsidair):
    - Full charge text
    - Legal article (Pasal and ayat)
    - Law reference (UU number and year)
    - Crime elements (unsur-unsur)

    Structure as hierarchical JSON with primary and alternative charges.
    """,

    "verdict": """
    Extract verdict and sentencing information from MENGADILI section:
    - verdict: GUILTY, NOT_GUILTY, or RELEASED
    - sentence_prison: Prison time (separate years and months)
    - sentence_fine: Fine amount in Rupiah (numeric only)
    - sentence_fine_alternative: Alternative imprisonment for unpaid fine
    - detention_deducted: Whether detention time is deducted
    - evidence_disposition: What happens to evidence

    Extract exactly as stated in the verdict.
    """,
}
```

### 4.3 Validation Rules Engine

```python
VALIDATION_RULES = {
    "case_number": {
        "required": True,
        "pattern": r"^\d+/(Pid|Pdt)\.[A-Za-z.]+/\d{4}/(PN|PT|MA)",
        "message": "Invalid case number format"
    },

    "defendant_nik": {
        "required": False,
        "pattern": r"^\d{16}$",
        "message": "NIK must be 16 digits"
    },

    "decision_date": {
        "required": True,
        "type": "date",
        "min": "1945-01-01",
        "max": "today",
        "message": "Invalid decision date"
    },

    "chronology": {
        "custom": "validate_date_sequence",
        "fields": ["incident_date", "arrest_date", "hearing_date_first",
                  "hearing_date_last", "decision_date"],
        "message": "Dates must be in chronological order"
    },

    "sentence_consistency": {
        "custom": "validate_sentence",
        "rule": "If verdict is GUILTY, must have prison or fine",
        "message": "Guilty verdict must include sentence"
    },

    "charge_verdict_match": {
        "custom": "validate_charge_proven",
        "rule": "charge_proven must match one of the charges",
        "message": "Proven charge not found in charge list"
    }
}

CROSS_FIELD_VALIDATION = {
    "age_calculation": {
        "fields": ["defendant_birth_date", "decision_date", "defendant_age"],
        "function": "validate_age_matches",
        "tolerance": 1  # year
    },

    "prison_total": {
        "fields": ["sentence_prison_years", "sentence_prison_months",
                  "sentence_prison_total_months"],
        "function": "validate_prison_calculation"
    },

    "court_level_appeal": {
        "fields": ["court_level", "previous_decision"],
        "function": "validate_appeal_hierarchy"
    }
}
```

### 4.4 Confidence Scoring

```python
CONFIDENCE_CALCULATION = {
    "factors": {
        "extraction_method": {
            "regex_match": 0.95,
            "llm_with_validation": 0.85,
            "llm_only": 0.70,
            "inferred": 0.50
        },

        "field_presence": {
            "explicit_label": 0.95,  # Field has clear label in doc
            "section_present": 0.85,  # Found in expected section
            "implicit_location": 0.70,  # Found elsewhere
            "not_found": 0.30  # Inferred or defaulted
        },

        "validation_status": {
            "all_rules_pass": 1.0,
            "minor_warnings": 0.90,
            "format_issues": 0.70,
            "validation_failed": 0.40
        },

        "cross_field_consistency": {
            "fully_consistent": 1.0,
            "minor_discrepancy": 0.85,
            "major_discrepancy": 0.60,
            "contradictory": 0.30
        },

        "llm_certainty": {
            "high": 0.95,
            "medium": 0.80,
            "low": 0.60
        }
    },

    "calculation": "weighted_average",
    "weights": {
        "extraction_method": 0.25,
        "field_presence": 0.20,
        "validation_status": 0.25,
        "cross_field_consistency": 0.20,
        "llm_certainty": 0.10
    }
}

REVIEW_TRIGGERS = {
    "critical_fields": {
        "threshold": 0.90,
        "fields": ["case_number", "defendant_name", "verdict",
                  "decision_date", "sentence_prison_total_months"]
    },

    "important_fields": {
        "threshold": 0.85,
        "fields": ["charge_primary_article", "charge_proven",
                  "prosecutor_name", "judge_presiding"]
    },

    "standard_fields": {
        "threshold": 0.75,
        "fields": ["defendant_occupation", "evidence_count",
                  "witness_count"]
    }
}
```

### 4.5 Indonesian Language Processing

```python
INDONESIAN_NLP_PIPELINE = {
    "tokenization": {
        "tool": "spaCy Indonesian model",
        "custom_rules": [
            "Preserve legal terms as single tokens: 'Terdakwa', 'Jaksa Penuntut Umum'",
            "Keep article references together: 'Pasal 114 ayat (2)'",
            "Preserve Indonesian names with 'Bin'/'Binti'"
        ]
    },

    "named_entity_recognition": {
        "entities": {
            "PERSON": ["defendants", "judges", "prosecutors", "witnesses"],
            "ORG": ["courts", "law_enforcement", "legal_offices"],
            "LOC": ["incident_locations", "addresses", "jurisdictions"],
            "DATE": ["decision_dates", "incident_dates", "hearing_dates"],
            "MONEY": ["fines", "compensation", "evidence_money"],
            "LAW": ["legal_articles", "regulations"]
        },
        "custom_patterns": [
            {"label": "LAW", "pattern": "Pasal \\d+( ayat \\(\\d+\\))?"},
            {"label": "LAW", "pattern": "UU (No\\.?|Nomor) \\d+ Tahun \\d{4}"},
            {"label": "CASE_NUMBER", "pattern": "\\d+/[A-Z][a-z]+\\.[A-Z][a-z.]+/\\d{4}/[A-Z]+"}
        ]
    },

    "legal_term_normalization": {
        "abbreviations": {
            "UU": "Undang-Undang",
            "PP": "Peraturan Pemerintah",
            "PN": "Pengadilan Negeri",
            "PT": "Pengadilan Tinggi",
            "MA": "Mahkamah Agung",
            "JPU": "Jaksa Penuntut Umum"
        },

        "terminology_standardization": {
            "terdakwa": "Terdakwa",
            "jaksa penuntut umum": "Jaksa Penuntut Umum",
            "mengadili": "MENGADILI",
            "dakwaan": "DAKWAAN"
        }
    },

    "date_parsing": {
        "formats": [
            "%d %B %Y",  # "15 Oktober 2023"
            "%d-%m-%Y",  # "15-10-2023"
            "%d/%m/%Y",  # "15/10/2023"
        ],
        "month_mapping": {
            "Januari": 1, "Februari": 2, "Maret": 3, "April": 4,
            "Mei": 5, "Juni": 6, "Juli": 7, "Agustus": 8,
            "September": 9, "Oktober": 10, "November": 11, "Desember": 12
        },
        "text_to_number": {
            "satu": 1, "dua": 2, "tiga": 3, "empat": 4,
            "lima": 5, "enam": 6, "tujuh": 7, "delapan": 8,
            "sembilan": 9, "sepuluh": 10,
            "dua puluh": 20, "tiga puluh": 30,
            "ribu": 1000, "juta": 1000000
        }
    },

    "currency_parsing": {
        "patterns": [
            r"Rp\.?\s*(\d+\.?\d*\.?\d*\.?\d*)",
            r"(\d+\.?\d*\.?\d*\.?\d*)\s*rupiah",
            r"sebesar\s*Rp\.?\s*(\d+\.?\d*\.?\d*\.?\d*)"
        ],
        "normalization": "remove_dots_convert_to_integer"
    }
}
```

---

## 5. Database Schema

### 5.1 Schema Organization

The database schema is organized into two schemas for clear separation of concerns:

**`public` Schema** - Shared configuration tables across all document sources:
- `document_sources` - Source registration and metadata
- `source_extraction_profiles` - Processing configurations per source
- `source_field_definitions` - Field definitions per source
- `source_normalization_rules` - Normalization rules per source
- `source_prompt_templates` - LLM prompt templates per source

**`id_sc` Schema** - ID_SC specific extraction results and processing data:
- `extraction_jobs` - Job tracking and status
- `extraction_results` - Field-level extraction results
- `approved_extractions` - Final approved structured data
- `document_segments` - Document segmentation data

### 5.2 Public Schema - Configuration Tables

These tables are shared across all document sources and reference the source via `source_id`.

```sql
-- Document source registration (shared across all sources)
CREATE TABLE IF NOT EXISTS public.document_sources (
    source_id VARCHAR(20) PRIMARY KEY, -- 'ID_SC', 'SG_SC', 'ID_LKPP', etc.
    source_name VARCHAR(200) NOT NULL,
    country_code VARCHAR(3),
    primary_language VARCHAR(10),
    secondary_languages VARCHAR(10)[],

    -- Document characteristics
    legal_system VARCHAR(50), -- 'civil_law', 'common_law', 'syariah'
    document_type VARCHAR(100), -- 'court_judgment', 'regulation', 'blacklist'

    -- Status
    is_active BOOLEAN DEFAULT true,
    phase INTEGER DEFAULT 1, -- Implementation phase

    -- Statistics
    total_documents_processed INTEGER DEFAULT 0,
    avg_accuracy DECIMAL(4,2),
    avg_cost_per_document DECIMAL(10,2),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Insert ID_SC source
INSERT INTO public.document_sources (source_id, source_name, country_code, primary_language, legal_system, document_type, phase)
VALUES ('ID_SC', 'Indonesian Supreme Court', 'IDN', 'id', 'civil_law', 'court_judgment', 1)
ON CONFLICT (source_id) DO NOTHING;

-- Source-specific extraction profiles
CREATE TABLE IF NOT EXISTS public.source_extraction_profiles (
    profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id VARCHAR(20) REFERENCES public.document_sources(source_id),
    profile_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false,

    -- Processing configuration
    pdf_extraction_method VARCHAR(50) DEFAULT 'pdfplumber', -- 'pdfplumber', 'pymupdf'
    ocr_threshold DECIMAL(3,2) DEFAULT 0.80, -- Trigger OCR if quality below this
    ocr_language VARCHAR(10), -- 'ind' for Indonesian
    use_document_ai_fallback BOOLEAN DEFAULT true,

    -- Segmentation strategy
    segmentation_method VARCHAR(50) DEFAULT 'section_based', -- 'section_based', 'fixed_token'
    segment_size_tokens INTEGER DEFAULT 3000,
    segment_overlap_tokens INTEGER DEFAULT 200,

    -- LLM configuration
    llm_model_quick VARCHAR(50) DEFAULT 'gemini-1.5-flash',
    llm_model_detailed VARCHAR(50) DEFAULT 'gemini-1.5-pro',
    llm_temperature DECIMAL(2,1) DEFAULT 0.1,
    max_retries INTEGER DEFAULT 2,

    -- Budget control
    max_cost_per_document DECIMAL(10,2) DEFAULT 2.00,
    enable_deep_dive_pass BOOLEAN DEFAULT true,
    deep_dive_confidence_threshold DECIMAL(3,2) DEFAULT 0.75,

    -- Version control
    version INTEGER DEFAULT 1,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(source_id, profile_name)
);

-- Field definitions per source
CREATE TABLE IF NOT EXISTS public.source_field_definitions (
    field_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id VARCHAR(20) REFERENCES public.document_sources(source_id),

    -- Field metadata
    field_name VARCHAR(100) NOT NULL,
    field_display_name VARCHAR(200),
    field_category VARCHAR(50), -- 'critical', 'important', 'standard', 'contextual'
    field_type VARCHAR(50), -- 'string', 'integer', 'date', 'boolean', 'text', 'bigint'

    -- Extraction configuration
    extraction_method VARCHAR(50), -- 'regex', 'llm', 'hybrid', 'calculated'
    extraction_section VARCHAR(100), -- Which document section to search
    regex_pattern TEXT,
    llm_prompt_template_id UUID, -- References source_prompt_templates

    -- Validation
    is_required BOOLEAN DEFAULT false,
    validation_rules JSONB,
    confidence_threshold DECIMAL(3,2) DEFAULT 0.75,

    -- Normalization
    normalization_rules JSONB,

    -- Display order
    display_order INTEGER,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(source_id, field_name)
);

-- Source-specific normalization rules
CREATE TABLE IF NOT EXISTS public.source_normalization_rules (
    rule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id VARCHAR(20) REFERENCES public.document_sources(source_id),
    rule_name VARCHAR(100) NOT NULL,
    rule_type VARCHAR(50), -- 'ocr_correction', 'legal_term', 'date', 'currency', 'name'

    -- Pattern matching
    pattern TEXT NOT NULL,
    replacement TEXT,
    is_regex BOOLEAN DEFAULT false,

    -- Applicability
    apply_to_sections VARCHAR(100)[], -- Which sections this applies to
    priority INTEGER DEFAULT 100,
    is_active BOOLEAN DEFAULT true,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Prompt templates per source
CREATE TABLE IF NOT EXISTS public.source_prompt_templates (
    template_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id VARCHAR(20) REFERENCES public.document_sources(source_id),
    template_name VARCHAR(100) NOT NULL,
    template_type VARCHAR(50), -- 'system', 'section', 'field', 'validation'
    language_code VARCHAR(10), -- 'id', 'en', etc.

    -- Template content
    prompt_text TEXT NOT NULL,
    variables JSONB, -- Available variables for template

    -- Performance tracking
    usage_count INTEGER DEFAULT 0,
    avg_confidence DECIMAL(3,2),
    avg_tokens_used INTEGER,

    is_active BOOLEAN DEFAULT true,
    version INTEGER DEFAULT 1,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(source_id, template_name, version)
);

-- Create indexes for configuration tables
CREATE INDEX idx_profiles_source ON public.source_extraction_profiles(source_id);
CREATE INDEX idx_profiles_active ON public.source_extraction_profiles(source_id, is_active);
CREATE INDEX idx_fields_source ON public.source_field_definitions(source_id);
CREATE INDEX idx_fields_category ON public.source_field_definitions(source_id, field_category);
CREATE INDEX idx_rules_source ON public.source_normalization_rules(source_id, is_active);
CREATE INDEX idx_templates_source ON public.source_prompt_templates(source_id, is_active);
```

### 5.3 ID_SC Schema - Extraction Results Tables

These tables are specific to Indonesian Supreme Court document processing.

```sql
-- Create id_sc schema
CREATE SCHEMA IF NOT EXISTS id_sc;

-- Main extraction job
CREATE TABLE IF NOT EXISTS id_sc.extraction_jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id VARCHAR(20) DEFAULT 'ID_SC',
    profile_id UUID REFERENCES public.source_extraction_profiles(profile_id),

    -- Document info
    document_id UUID NOT NULL,
    document_url TEXT,
    gcs_path TEXT,

    -- Processing status
    status VARCHAR(50) DEFAULT 'queued', -- 'queued', 'processing', 'completed', 'failed', 'review_required'
    current_stage VARCHAR(50),
    progress_percentage INTEGER DEFAULT 0,

    -- Document characteristics
    page_count INTEGER,
    is_scanned BOOLEAN,
    ocr_used BOOLEAN DEFAULT false,
    language_detected VARCHAR(10) DEFAULT 'id',

    -- Processing metrics
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    total_duration_seconds INTEGER,

    -- Cost tracking
    cost_pdf_extraction DECIMAL(10,4) DEFAULT 0,
    cost_ocr DECIMAL(10,4) DEFAULT 0,
    cost_llm_quick DECIMAL(10,4) DEFAULT 0,
    cost_llm_detailed DECIMAL(10,4) DEFAULT 0,
    cost_llm_validation DECIMAL(10,4) DEFAULT 0,
    cost_total DECIMAL(10,4) GENERATED ALWAYS AS (
        cost_pdf_extraction + cost_ocr + cost_llm_quick +
        cost_llm_detailed + cost_llm_validation
    ) STORED,

    -- Tokens
    tokens_used_total INTEGER DEFAULT 0,

    -- Error handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,

    -- Review
    requires_review BOOLEAN DEFAULT false,
    review_priority INTEGER, -- 1-10
    review_completed_at TIMESTAMP,
    reviewed_by UUID,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Extracted field results
CREATE TABLE IF NOT EXISTS id_sc.extraction_results (
    result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES id_sc.extraction_jobs(job_id) ON DELETE CASCADE,
    field_id UUID REFERENCES public.source_field_definitions(field_id),

    -- Field identification
    field_name VARCHAR(100),
    field_category VARCHAR(50),

    -- Extraction attempts (can have multiple)
    extraction_pass INTEGER, -- 1=quick, 2=detailed, 3=validation, 4=deep_dive
    extraction_method VARCHAR(50),

    -- Extracted value
    value_raw TEXT, -- As extracted
    value_normalized JSONB, -- After normalization
    value_type VARCHAR(50),

    -- Confidence and validation
    confidence_score DECIMAL(3,2),
    confidence_factors JSONB, -- Breakdown of confidence calculation
    validation_status VARCHAR(50), -- 'passed', 'warning', 'failed'
    validation_messages JSONB,

    -- Source location in document
    found_in_section VARCHAR(100),
    found_on_page INTEGER,
    source_text_snippet TEXT,

    -- Selection
    is_selected BOOLEAN DEFAULT false,
    selection_reason TEXT,

    -- Review
    flagged_for_review BOOLEAN DEFAULT false,
    review_status VARCHAR(50), -- 'pending', 'approved', 'corrected', 'rejected'
    corrected_value JSONB,
    review_notes TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);

-- Final approved results (one per job)
CREATE TABLE IF NOT EXISTS id_sc.approved_extractions (
    extraction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES id_sc.extraction_jobs(job_id) ON DELETE CASCADE,

    -- Document & Court Information (9 fields)
    sequence_number INTEGER,
    case_registration_number VARCHAR(100),
    verdict_number VARCHAR(100),
    verdict_date DATE,
    verdict_year INTEGER,
    verdict_day_of_week VARCHAR(20),
    court_region VARCHAR(100),
    province VARCHAR(100),
    verdict_ruling_date DATE,
    verdict_ruling_day_of_week VARCHAR(20),

    -- Defendant Information (10 fields)
    defendant_name VARCHAR(200),
    defendant_birth_place VARCHAR(100),
    defendant_birth_date DATE,
    defendant_age INTEGER,
    defendant_gender VARCHAR(20),
    defendant_nationality VARCHAR(50),
    defendant_address TEXT,
    defendant_religion VARCHAR(50),
    defendant_occupation VARCHAR(100),
    defendant_education VARCHAR(50),

    -- Pre-Trial Detention (5 fields)
    detention_start_date DATE,
    detention_end_date DATE, -- Auto-adjusted: if > verdict_date, set to verdict_date
    detention_duration_days INTEGER,
    detention_type VARCHAR(100),
    detention_deducted BOOLEAN DEFAULT true,

    -- Legal Representatives (4 fields)
    defense_lawyer_name TEXT, -- Can be multiple lawyers
    defense_lawyer_office_address TEXT,
    prosecutor_name TEXT,
    court_clerk_name VARCHAR(200),
    judge_name TEXT, -- Can be array

    -- Charge Information - Dakwaan (9 fields)
    charge_chronology TEXT,
    crime_location TEXT,
    crime_time_period VARCHAR(200),
    state_loss_charged BIGINT,
    article_charged_first VARCHAR(200),
    article_charged_second VARCHAR(200),
    article_charged_third VARCHAR(200),
    article_charged_fourth VARCHAR(200),
    charge_structure_type VARCHAR(50),
    defense_objection TEXT,

    -- Prosecution Demands - Tuntutan (7 fields)
    prosecution_demand_date DATE,
    prosecution_article VARCHAR(300),
    prosecution_demand_content TEXT,
    prosecution_prison_demand VARCHAR(100),
    prosecution_prison_type VARCHAR(20),
    prosecution_prison_months INTEGER,
    prosecution_fine_demand BIGINT,
    prosecution_restitution_demand BIGINT,
    prosecution_restitution_alternative VARCHAR(100),
    prosecution_restitution_alternative_months INTEGER,

    -- Verdict Information - Amar (16 fields)
    legal_facts TEXT,
    verdict_article VARCHAR(200),
    verdict_article_conjunction_1 VARCHAR(200),
    verdict_article_conjunction_2 VARCHAR(200),
    verdict_content TEXT,
    verdict_prison_sentence VARCHAR(100),
    verdict_prison_type VARCHAR(20),
    verdict_prison_total_months INTEGER,
    verdict_fine_amount BIGINT,
    verdict_restitution_amount BIGINT,
    verdict_restitution_alternative VARCHAR(100),
    verdict_restitution_alternative_months INTEGER,
    state_loss_recovered BIGINT,
    corruption_proceeds BIGINT,
    remaining_restitution BIGINT,
    state_loss_verdict BIGINT,
    state_loss_auditor VARCHAR(100),

    -- Mitigating & Aggravating Factors (12 fields)
    aggravating_factor_1 TEXT,
    aggravating_factor_2 TEXT,
    aggravating_factor_3 TEXT,
    aggravating_factor_4 TEXT,
    aggravating_factor_5 TEXT,
    mitigating_factor_1 TEXT,
    mitigating_factor_2 TEXT,
    mitigating_factor_3 TEXT,
    mitigating_factor_4 TEXT,
    mitigating_factor_5 TEXT,
    mitigating_factor_6 TEXT,
    mitigating_factor_7 TEXT,

    -- Store all fields as JSONB for flexibility
    all_fields_json JSONB NOT NULL,

    -- Quality metrics
    overall_confidence DECIMAL(3,2),
    fields_requiring_review INTEGER,
    fields_corrected INTEGER,

    -- Approval
    approved_at TIMESTAMP DEFAULT NOW(),
    approved_by UUID,

    -- Export
    exported BOOLEAN DEFAULT false,
    exported_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT NOW()
);

-- Document segments
CREATE TABLE IF NOT EXISTS id_sc.document_segments (
    segment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES id_sc.extraction_jobs(job_id) ON DELETE CASCADE,

    -- Segment identification
    section_name VARCHAR(100), -- 'header', 'defendant', 'charges', etc.
    segment_index INTEGER,

    -- Content
    text_original TEXT,
    text_normalized TEXT,
    token_count INTEGER,

    -- Location
    start_page INTEGER,
    end_page INTEGER,
    start_position INTEGER,
    end_position INTEGER,

    -- Processing
    processed BOOLEAN DEFAULT false,
    llm_model_used VARCHAR(50),
    tokens_used INTEGER,
    cost DECIMAL(10,4),

    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for id_sc schema tables
CREATE INDEX IF NOT EXISTS idx_jobs_status ON id_sc.extraction_jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_created ON id_sc.extraction_jobs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_source ON id_sc.extraction_jobs(source_id, status);
CREATE INDEX IF NOT EXISTS idx_results_job ON id_sc.extraction_results(job_id);
CREATE INDEX IF NOT EXISTS idx_results_field ON id_sc.extraction_results(field_name);
CREATE INDEX IF NOT EXISTS idx_results_review ON id_sc.extraction_results(flagged_for_review)
    WHERE flagged_for_review = true;
CREATE INDEX IF NOT EXISTS idx_approved_case_number ON id_sc.approved_extractions(case_registration_number);
CREATE INDEX IF NOT EXISTS idx_approved_defendant ON id_sc.approved_extractions(defendant_name);
CREATE INDEX IF NOT EXISTS idx_approved_date ON id_sc.approved_extractions(verdict_date);
CREATE INDEX IF NOT EXISTS idx_segments_job ON id_sc.document_segments(job_id);
```

### 5.4 Schema Separation Benefits

This schema architecture provides several advantages:

**Configuration Sharing**
- All document sources (ID_SC, SG_SC, ID_LKPP, etc.) share configuration tables in `public` schema
- Single source of truth for extraction profiles, field definitions, and rules
- Reduces duplication and simplifies configuration management
- Easy to compare configurations across sources

**Source Isolation**
- Each source has its own schema for extraction results (e.g., `id_sc`, `sg_sc`)
- Source-specific tables don't interfere with each other
- Enables independent schema evolution per source
- Simplified access control per source

**Scalability**
- Can partition source-specific tables independently
- Can backup/restore individual source data
- Can archive old extraction results per source
- Can set different retention policies per source

**Maintainability**
- Clear separation between configuration (shared) and data (per-source)
- Easy to add new sources without modifying existing schemas
- Reduced risk of cross-source data corruption
- Simplified migrations for individual sources

**Example Access Patterns**

```sql
-- Get all active profiles for ID_SC
SELECT * FROM public.source_extraction_profiles
WHERE source_id = 'ID_SC' AND is_active = true;

-- Get ID_SC extraction jobs with results
SELECT j.*, e.*
FROM id_sc.extraction_jobs j
JOIN id_sc.extraction_results e ON j.job_id = e.job_id
WHERE j.status = 'completed';

-- Compare field definitions across sources
SELECT source_id, field_name, field_category, confidence_threshold
FROM public.source_field_definitions
WHERE field_name IN ('defendant_name', 'case_number')
ORDER BY source_id, field_name;
```

---

## 6. API Endpoints

### 6.1 Job Management

```
POST /api/v1/dataminer/id_sc/jobs
Submit new extraction job for ID_SC document

Request:
{
    "document_url": "https://example.com/doc.pdf",
    "profile_id": "uuid", // optional, uses default if not specified
    "priority": 5, // 1-10
    "metadata": {
        "source": "crawler",
        "crawled_at": "2024-01-15T10:00:00Z"
    },
    "options": {
        "force_ocr": false,
        "skip_validation": false,
        "fields_to_extract": [] // empty = all fields
    }
}

Response:
{
    "job_id": "uuid",
    "status": "queued",
    "estimated_cost": 1.50,
    "estimated_duration_minutes": 3,
    "position_in_queue": 5
}
```

```
GET /api/v1/dataminer/id_sc/jobs/{job_id}
Get job status and details

Response:
{
    "job_id": "uuid",
    "status": "processing",
    "current_stage": "llm_extraction_detailed",
    "progress_percentage": 65,
    "processing_time_elapsed_seconds": 120,
    "cost_so_far": 1.20,
    "estimated_completion_minutes": 2,
    "metrics": {
        "pages_processed": 45,
        "total_pages": 67,
        "fields_extracted": 52,
        "fields_requiring_review": 8
    }
}
```

```
GET /api/v1/dataminer/id_sc/jobs/{job_id}/results
Get extraction results

Response:
{
    "job_id": "uuid",
    "status": "completed",
    "overall_confidence": 0.87,
    "requires_review": true,
    "fields": {
        "case_number": {
            "value": "123/Pid.Sus/2023/PN Jkt.Pst",
            "confidence": 0.95,
            "validation_status": "passed",
            "review_required": false
        },
        "defendant_name": {
            "value": "AHMAD BIN HASAN",
            "confidence": 0.92,
            "validation_status": "passed",
            "review_required": false
        },
        "defendant_nik": {
            "value": "3174012345670001",
            "confidence": 0.68,
            "validation_status": "warning",
            "validation_message": "NIK format valid but could not verify checksum",
            "review_required": true
        },
        // ... all 65+ fields
    },
    "cost_breakdown": {
        "pdf_extraction": 0.05,
        "ocr": 0.00,
        "llm_quick": 0.15,
        "llm_detailed": 0.95,
        "llm_validation": 0.10,
        "total": 1.25
    }
}
```

### 6.2 Review Management

```
GET /api/v1/dataminer/id_sc/review/queue
Get review queue

Query params:
- priority_min: 1-10
- created_after: ISO datetime
- limit: integer
- offset: integer

Response:
{
    "total_count": 45,
    "items": [
        {
            "job_id": "uuid",
            "case_number": "123/Pid.Sus/2023/PN Jkt.Pst",
            "defendant_name": "AHMAD BIN HASAN",
            "review_priority": 8,
            "fields_requiring_review": 5,
            "created_at": "2024-01-15T10:00:00Z",
            "flagged_fields": [
                "defendant_nik",
                "sentence_fine_amount",
                "prosecutor_name"
            ]
        }
    ]
}
```

```
POST /api/v1/dataminer/id_sc/review/{job_id}/submit
Submit review corrections

Request:
{
    "reviewer_id": "uuid",
    "field_corrections": {
        "defendant_nik": {
            "action": "correct",
            "corrected_value": "3174012345670002",
            "notes": "Last digit was misread by OCR"
        },
        "sentence_fine_amount": {
            "action": "approve",
            "notes": "Verified against document"
        },
        "prosecutor_name": {
            "action": "reject",
            "notes": "Could not find in document"
        }
    },
    "overall_notes": "Good extraction overall, minor OCR issues"
}

Response:
{
    "review_id": "uuid",
    "job_id": "uuid",
    "fields_corrected": 1,
    "fields_approved": 1,
    "fields_rejected": 1,
    "job_status": "review_completed",
    "ready_for_export": true
}
```

### 6.3 Configuration Management

```
GET /api/v1/dataminer/id_sc/profiles
List extraction profiles

Response:
{
    "profiles": [
        {
            "profile_id": "uuid",
            "profile_name": "ID_SC Default Profile",
            "is_active": true,
            "llm_model_detailed": "gemini-1.5-pro",
            "avg_cost_per_document": 1.35,
            "avg_accuracy": 0.87,
            "total_documents_processed": 450
        }
    ]
}
```

```
POST /api/v1/dataminer/id_sc/fields
Add new field definition

Request:
{
    "field_name": "custom_field_name",
    "field_category": "contextual",
    "field_type": "string",
    "extraction_method": "llm",
    "extraction_section": "PERTIMBANGAN",
    "llm_prompt_template": "Extract the court's reasoning about...",
    "confidence_threshold": 0.70,
    "validation_rules": {
        "max_length": 500
    }
}
```

---

## 7. Quality Assurance

### 7.1 Accuracy Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Critical Field Accuracy** | >90% | Manual review of 100-doc sample |
| **Overall Field Accuracy** | >85% | Automated validation + review |
| **Case Number Extraction** | >98% | Regex validation |
| **Defendant Name Accuracy** | >90% | Manual review |
| **Verdict Extraction** | >95% | Keyword validation |
| **Sentence Amount Accuracy** | >92% | Cross-check with prosecutor demand |
| **Date Field Accuracy** | >88% | Format validation + logic checks |
| **Legal Citation Accuracy** | >85% | Format validation |

### 7.2 Performance Metrics

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| **Avg Processing Time** | <5 min/doc | >8 min |
| **Avg Cost per Document** | <$1.50 | >$2.50 |
| **OCR Usage Rate** | <20% | >30% |
| **Review Rate** | <25% | >40% |
| **Processing Success Rate** | >95% | <90% |
| **Same-day Completion** | >90% | <80% |

### 7.3 Testing Strategy

#### Unit Tests
- Text normalization functions
- Date parsing (all Indonesian formats)
- Currency extraction
- Legal citation parsing
- Validation rules
- Confidence calculation

#### Integration Tests
- End-to-end extraction pipeline
- LLM prompt effectiveness
- Section segmentation accuracy
- Multi-pass extraction flow
- Review workflow

#### Test Dataset
- 100 diverse ID_SC documents
- Coverage across:
  - Court levels: PN (40), PT (30), MA (30)
  - Case types: Pidana (70), Perdata (30)
  - Document quality: High (60), Medium (25), Low (15)
  - Years: 2018-2024
  - Different courts: 20+ jurisdictions

#### Validation Approach
1. **Gold Standard**: Manual annotation of 100 documents
2. **Baseline Testing**: Run extraction on test set
3. **Accuracy Calculation**: Field-by-field comparison
4. **Error Analysis**: Categorize extraction failures
5. **Iterative Improvement**: Adjust prompts, rules, thresholds
6. **Regression Testing**: Ensure improvements don't break existing accuracy

---

## 8. Deployment & Operations

### 8.1 Infrastructure

```yaml
Service: dataminer-id-sc
Deployment: Dokploy on dedicated VPS (dataminer-1)

Resources:
  CPU: 4 cores
  Memory: 16GB
  Storage: 200GB SSD

Docker Compose:
  services:
    - api: FastAPI application
    - worker: NATS consumer for processing
    - redis: Caching and job state
    - postgres: Configuration and results

External Services:
  - GCS: Document storage
  - Vertex AI: Gemini models
  - Google Document AI: OCR fallback
  - NATS JetStream: Job queue
```

### 8.2 Monitoring

```yaml
Metrics (Prometheus):
  - dataminer_id_sc_jobs_total{status}
  - dataminer_id_sc_processing_duration_seconds
  - dataminer_id_sc_cost_per_document
  - dataminer_id_sc_field_accuracy{field_name}
  - dataminer_id_sc_review_queue_size
  - dataminer_id_sc_ocr_usage_rate

Alerts:
  - High processing time (>10 min)
  - High cost per document (>$3)
  - High error rate (>5%)
  - Review queue backlog (>50)
  - Low confidence rate (>30% of docs)

Dashboards:
  - Operations: Job status, queue, throughput
  - Quality: Accuracy trends, confidence distributions
  - Cost: Per-document cost, budget tracking
```

### 8.3 Error Handling

```python
ERROR_HANDLING_STRATEGY = {
    "pdf_extraction_failed": {
        "retry": True,
        "max_retries": 2,
        "fallback": "force_ocr",
        "alert": False
    },

    "ocr_failed": {
        "retry": True,
        "max_retries": 1,
        "fallback": "use_document_ai",
        "alert": True  # Alert if Document AI also fails
    },

    "llm_rate_limit": {
        "retry": True,
        "max_retries": 3,
        "backoff": "exponential",
        "alert": False
    },

    "llm_timeout": {
        "retry": True,
        "max_retries": 2,
        "reduce_segment_size": True,
        "alert": True  # if repeated
    },

    "validation_failed": {
        "retry": False,
        "action": "flag_for_review",
        "alert": False
    },

    "budget_exceeded": {
        "retry": False,
        "action": "pause_job",
        "alert": True,
        "requires_manual_review": True
    }
}
```

---

## 9. Success Criteria

### 9.1 Phase 1 Goals (Month 1-2)

- [ ] Extract all 72 fields for corruption cases with >80% accuracy
- [ ] Process 10 ID_SC documents daily (focus on corruption cases)
- [ ] Maintain average cost <$1.50 per document
- [ ] Review workflow operational
- [ ] Critical fields (court info, defendant, verdict) >90% accuracy
- [ ] Financial fields (kerugian negara, uang pengganti) >85% accuracy
- [ ] API endpoints functional
- [ ] Monitoring dashboards live

### 9.2 Phase 2 Goals (Month 3-4)

- [ ] Increase accuracy to >85% overall
- [ ] Process 20 documents daily
- [ ] Critical fields >90% accuracy
- [ ] Review rate <25%
- [ ] Average processing time <4 minutes
- [ ] Learning from corrections improving accuracy

### 9.3 Production Ready Criteria

- [ ] 100-document test set: >85% accuracy
- [ ] Cost per document: <$2 average, <$5 maximum
- [ ] Processing reliability: >95% success rate
- [ ] Review interface: Efficient and user-friendly
- [ ] Documentation: Complete and accurate
- [ ] Monitoring: All metrics tracked
- [ ] Error handling: Graceful degradation
- [ ] Data security: Encryption and access control

---

## 10. Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| **OCR Quality for Scanned Docs** | High | Medium | Use Document AI for critical docs, manual review for low confidence |
| **Indonesian Legal Term Variations** | Medium | High | Build comprehensive terminology database, involve legal experts |
| **Complex Hierarchical Charges** | Medium | Medium | Specialized prompts for Dakwaan section, multi-pass extraction |
| **LLM Hallucination** | High | Low | Multi-pass validation, cross-field consistency checks, review workflow |
| **Budget Overruns** | Medium | Low | Real-time cost tracking, automatic pause at thresholds |
| **Processing Bottlenecks** | Low | Medium | Horizontal scaling, queue prioritization |
| **Data Quality Variance** | Medium | High | Quality detection, adaptive processing strategies |

---

## 11. Future Enhancements

### 11.1 Near-term (3-6 months)
- Active learning from manual corrections
- Automated terminology database expansion
- Enhanced entity extraction (addresses, organizations)
- Cross-reference resolution within documents
- Batch processing optimization

### 11.2 Long-term (6-12 months)
- Fine-tuned model for Indonesian legal text
- Automated quality assessment without manual review
- Relationship extraction (case citations, related cases)
- Predictive fields based on patterns
- Integration with legal knowledge graph

---

## 12. Appendices

### 12.1 Indonesian Legal System Reference

**Court Hierarchy:**
1. **Mahkamah Agung (MA)** - Supreme Court (cassation)
2. **Pengadilan Tinggi (PT)** - High Court (appeal)
3. **Pengadilan Negeri (PN)** - District Court (first instance)

**Case Type Codes:**
- Pid.Sus - Special Criminal (narcotics, corruption, terrorism)
- Pid.B - Regular Criminal
- Pdt.G - Civil Lawsuit
- Pdt.P - Civil Petition

**Common Legal Articles:**
- UU No. 35 Tahun 2009 - Narcotics Law
- UU No. 31 Tahun 1999 jo UU No. 20 Tahun 2001 - Corruption Law
- KUHP - Penal Code (Kitab Undang-Undang Hukum Pidana)
- KUHPerdata - Civil Code

### 12.2 Sample Extraction Output (Corruption Case)

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "document_id": "id_sc_123456",
  "source": "ID_SC",
  "extraction_date": "2024-01-15T10:30:00Z",
  "overall_confidence": 0.87,
  "document_type": "Tindak Pidana Korupsi",

  "document_court_info": {
    "sequence_number": 1,
    "case_registration_number": "45/Pid.Sus-TPK/2023/PN Jkt.Pst",
    "verdict_number": "45/Pid.Sus-TPK/2023/PN Jkt.Pst",
    "verdict_date": "2023-10-15",
    "verdict_year": 2023,
    "verdict_day_of_week": "Rabu",
    "court_region": "Jakarta Pusat",
    "province": "DKI Jakarta",
    "verdict_ruling_date": "2023-10-15",
    "verdict_ruling_day_of_week": "Rabu"
  },

  "defendant_info": {
    "defendant_name": "BUDI SANTOSO, S.E.",
    "defendant_birth_place": "Jakarta",
    "defendant_birth_date": "1975-03-20",
    "defendant_age": 48,
    "defendant_gender": "Laki-laki",
    "defendant_nationality": "Indonesia",
    "defendant_address": "Jl. Gatot Subroto No. 45, Jakarta Selatan",
    "defendant_religion": "Islam",
    "defendant_occupation": "Kepala Dinas Pekerjaan Umum Kota XYZ",
    "defendant_education": "S1 Teknik Sipil"
  },

  "pre_trial_detention": {
    "detention_start_date": "2020-03-15",
    "detention_end_date": "2023-10-15",
    "detention_end_date_note": "Adjusted to verdict_date (was 2023-11-20)",
    "detention_duration_days": 1310,
    "detention_type": "Rutan",
    "detention_deducted": true
  },

  "legal_representatives": {
    "defense_lawyer_name": "Ahmad Budiman, S.H., M.H. dan Siti Rahma, S.H.",
    "defense_lawyer_office_address": "Kantor Hukum Budiman & Partners, Jl. Thamrin No. 10, Jakarta Pusat",
    "prosecutor_name": "Andi Wijaya, S.H. dan Rini Susanti, S.H.",
    "court_clerk_name": "Hendra Gunawan",
    "judge_name": "Dr. Bambang Sutrisno, S.H., M.H. (Ketua), Siti Aminah, S.H., Ahmad Fauzi, S.H. (Anggota)"
  },

  "charges": {
    "charge_chronology": "Bahwa terdakwa pada periode Januari 2020 sampai dengan Maret 2021, selaku Kepala Dinas Pekerjaan Umum, telah menyalahgunakan kewenangannya dengan melakukan mark-up harga dalam proyek pembangunan jalan...",
    "crime_location": "Kantor Dinas Pekerjaan Umum Kota XYZ, Provinsi ABC",
    "crime_time_period": "Januari 2020 - Maret 2021",
    "state_loss_charged": 5000000000,
    "article_charged_first": "Pasal 2 ayat (1)",
    "article_charged_second": "Pasal 3",
    "article_charged_third": "Pasal 18",
    "article_charged_fourth": null,
    "charge_structure_type": "Subsidair",
    "defense_objection": null
  },

  "prosecution_demands": {
    "prosecution_demand_date": "2023-09-20",
    "prosecution_article": "Pasal 2 ayat (1) jo. Pasal 18 UU No. 31 Tahun 1999 jo. UU No. 20 Tahun 2001",
    "prosecution_demand_content": "Menyatakan terdakwa BUDI SANTOSO, S.E. terbukti bersalah melakukan tindak pidana korupsi sebagaimana diatur dalam Pasal 2 ayat (1)...",
    "prosecution_prison_demand": "6 tahun penjara",
    "prosecution_prison_type": "Penjara",
    "prosecution_prison_months": 72,
    "prosecution_fine_demand": 500000000,
    "prosecution_restitution_demand": 3500000000,
    "prosecution_restitution_alternative": "1 tahun penjara",
    "prosecution_restitution_alternative_months": 12
  },

  "verdict_ruling": {
    "legal_facts": "Berdasarkan fakta-fakta di persidangan, terdakwa selaku Kepala Dinas telah menyalahgunakan kewenangannya dengan melakukan mark-up harga proyek...",
    "verdict_article": "Pasal 2 ayat (1)",
    "verdict_article_conjunction_1": "Pasal 18",
    "verdict_article_conjunction_2": "UU No. 31 Tahun 1999 jo. UU No. 20 Tahun 2001 tentang Pemberantasan Tindak Pidana Korupsi",
    "verdict_content": "1. Menyatakan terdakwa BUDI SANTOSO, S.E. telah terbukti secara sah dan meyakinkan bersalah melakukan tindak pidana korupsi; 2. Menjatuhkan pidana terhadap terdakwa...",
    "verdict_prison_sentence": "4 tahun 6 bulan penjara",
    "verdict_prison_type": "Penjara",
    "verdict_prison_total_months": 54,
    "verdict_fine_amount": 200000000,
    "verdict_restitution_amount": 2500000000,
    "verdict_restitution_alternative": "6 bulan penjara",
    "verdict_restitution_alternative_months": 6,
    "state_loss_recovered": 500000000,
    "corruption_proceeds": 3000000000,
    "remaining_restitution": 2000000000,
    "state_loss_verdict": 2500000000,
    "state_loss_auditor": "BPKP"
  },

  "sentencing_considerations": {
    "aggravating_factors": [
      "Perbuatan terdakwa sangat merugikan keuangan negara",
      "Perbuatan terdakwa tidak mendukung program pemerintah dalam pemberantasan korupsi"
    ],
    "mitigating_factors": [
      "Terdakwa bersikap sopan di persidangan",
      "Terdakwa belum pernah dihukum",
      "Terdakwa menyesali perbuatannya",
      "Terdakwa memiliki tanggungan keluarga",
      "Terdakwa telah mengembalikan sebagian kerugian negara"
    ]
  },

  "processing_metadata": {
    "pages_processed": 125,
    "ocr_used": false,
    "processing_time_seconds": 287,
    "cost_breakdown": {
      "pdf_extraction": 0.08,
      "llm_quick_scan": 0.18,
      "llm_detailed": 1.15,
      "llm_validation": 0.12,
      "total": 1.53
    },
    "fields_extracted": 72,
    "fields_requiring_review": 6,
    "confidence_distribution": {
      "high_confidence_90_plus": 58,
      "medium_confidence_75_90": 10,
      "low_confidence_below_75": 4
    }
  }
}
```

---

**Document Version:** 1.0
**Last Updated:** 2024-01-15
**Status:** Ready for Implementation
**Approval:** Pending
