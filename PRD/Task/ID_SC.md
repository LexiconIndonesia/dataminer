# ID_SC Specific Tasks - Indonesian Supreme Court

**Source ID:** ID_SC
**Status:** Phase 1 - Implementation
**Last Updated:** 2024-11-24
**Total Fields:** 77 fields

---

## 1. ID_SC Schema Setup

### Task 1.1: Create ID_SC Schema and Tables

**Actionable Items:**
- [ ] Create `id_sc` schema in PostgreSQL
- [ ] Create migration for `id_sc.extraction_jobs` table
- [ ] Create migration for `id_sc.extraction_results` table
- [ ] Create migration for `id_sc.approved_extractions` table with all 77 fields
- [ ] Create migration for `id_sc.document_segments` table
- [ ] Add all indexes for performance optimization
- [ ] Add foreign key constraints to public schema
- [ ] Test CASCADE delete behavior

**Positive Cases:**
- Successfully create id_sc schema
- Create all tables without errors
- Insert job record successfully
- Insert extraction results for multiple fields
- Insert approved extraction with all 77 fields populated
- Foreign keys properly reference public.source_extraction_profiles

**Negative Cases:**
- Handle duplicate job_id insertion
- Reject invalid profile_id reference
- Handle constraint violations for BIGINT fields (financial amounts)
- Prevent deletion of job with existing results

**Edge Cases:**
- Job with 0 extraction results (failed extraction)
- Approved extraction with many NULL fields (partial extraction)
- Very large TEXT fields (>100KB for charge_chronology)
- BIGINT financial amounts (>1 trillion Rupiah)
- Multi-value fields with semicolon separator

**Unit Tests:**
```python
def test_create_extraction_job():
    """Test creating ID_SC extraction job"""
    job = create_id_sc_job(
        source_id="ID_SC",
        profile_id=get_default_profile("ID_SC").profile_id,
        document_url="https://example.com/doc.pdf",
        gcs_path="gs://bucket/doc.pdf"
    )
    assert job.source_id == "ID_SC"
    assert job.status == "queued"

def test_insert_extraction_result():
    """Test inserting field extraction result"""
    job = create_id_sc_job(...)
    result = create_extraction_result(
        job_id=job.job_id,
        field_name="defendant_name",
        value_raw="AHMAD BIN HASAN",
        confidence_score=0.92
    )
    assert result.field_name == "defendant_name"
    assert result.confidence_score == 0.92

def test_approved_extraction_all_fields():
    """Test inserting approved extraction with all 77 fields"""
    job = create_id_sc_job(...)

    approved = create_approved_extraction(
        job_id=job.job_id,
        case_registration_number="45/Pid.Sus-TPK/2023/PN Jkt.Pst",
        verdict_date="2023-10-15",
        defendant_name="BUDI SANTOSO",
        verdict_prison_total_months=54,
        verdict_restitution_amount=2500000000,  # BIGINT
        # ... all 77 fields
    )
    assert approved.verdict_restitution_amount == 2500000000

def test_cascade_delete():
    """Test CASCADE delete behavior"""
    job = create_id_sc_job(...)
    create_extraction_result(job_id=job.job_id, ...)
    create_approved_extraction(job_id=job.job_id, ...)

    # Delete job
    delete_job(job.job_id)

    # Results and approved should be deleted
    assert get_extraction_results(job.job_id) == []
    assert get_approved_extraction(job.job_id) is None

def test_multi_value_field_storage():
    """Test storing multi-value fields with semicolon separator"""
    approved = create_approved_extraction(
        defense_lawyer_name="Ahmad Budiman, S.H.; Siti Rahma, S.H., M.H.",
        prosecutor_name="Andi Wijaya, S.H.; Rini Susanti, S.H.",
        judge_name="Bambang, S.H. (Ketua); Siti, S.H.; Ahmad, S.H."
    )
    assert ";" in approved.defense_lawyer_name
    assert approved.defense_lawyer_name.count(";") == 1
```

---

## 2. Indonesian Language Processing

### Task 2.1: Indonesian NLP Pipeline

**Actionable Items:**
- [ ] Set up spaCy Indonesian model
- [ ] Implement Indonesian date parser (text to ISO format)
- [ ] Implement Indonesian currency parser (Rupiah)
- [ ] Implement Indonesian legal term tokenizer
- [ ] Add Indonesian stopwords handling
- [ ] Implement name extraction (with Bin/Binti handling)
- [ ] Add Indonesian day-of-week mapping
- [ ] Implement Indonesian number-to-digit conversion

**Positive Cases:**
- Parse Indonesian date: "Lima Belas Oktober Dua Ribu Dua Puluh Tiga" ’ "2023-10-15"
- Parse Indonesian day: "Rabu" ’ "Wednesday"
- Parse currency: "Rp. 5.000.000.000,-" ’ 5000000000
- Extract names: "AHMAD BIN HASAN" (preserve "Bin")
- Parse sentence duration: "4 tahun 6 bulan" ’ 54 months
- Recognize legal terms: "Terdakwa", "Jaksa Penuntut Umum", "MENGADILI"

**Negative Cases:**
- Handle invalid date strings
- Handle malformed currency values
- Handle non-Indonesian text
- Handle mixed language content

**Edge Cases:**
- Date without year (assume current year)
- Currency with missing "Rp." prefix
- Names with multiple "Bin" (AHMAD BIN HASAN BIN ALI)
- Very long names (>200 characters)
- Legal terms with typos (OCR errors)

**Unit Tests:**
```python
def test_parse_indonesian_date():
    """Test parsing Indonesian date to ISO format"""
    # Full text date
    date = parse_indonesian_date("Lima Belas Oktober Dua Ribu Dua Puluh Tiga")
    assert date == "2023-10-15"

    # Numeric format
    date = parse_indonesian_date("15 Oktober 2023")
    assert date == "2023-10-15"

    # Short format
    date = parse_indonesian_date("15-10-2023")
    assert date == "2023-10-15"

def test_parse_rupiah_amount():
    """Test parsing Rupiah currency amounts"""
    # With Rp. prefix and separators
    amount = parse_rupiah("Rp. 5.000.000.000,-")
    assert amount == 5000000000

    # Without separators
    amount = parse_rupiah("Rp 5000000000")
    assert amount == 5000000000

    # Text amount
    amount = parse_rupiah("lima miliar rupiah")
    assert amount == 5000000000

def test_parse_prison_duration():
    """Test parsing prison sentence duration to months"""
    # Years and months
    months = parse_prison_duration("4 tahun 6 bulan penjara")
    assert months == 54

    # Only years
    months = parse_prison_duration("5 tahun penjara")
    assert months == 60

    # Only months
    months = parse_prison_duration("18 bulan penjara")
    assert months == 18

def test_extract_indonesian_name():
    """Test extracting Indonesian names with Bin/Binti"""
    name = extract_name("Terdakwa AHMAD BIN HASAN dilahirkan")
    assert name == "AHMAD BIN HASAN"

    name = extract_name("SITI BINTI RAHMAN")
    assert name == "SITI BINTI RAHMAN"

def test_day_of_week_mapping():
    """Test Indonesian day of week mapping"""
    assert indonesian_day_to_english("Senin") == "Monday"
    assert indonesian_day_to_english("Selasa") == "Tuesday"
    assert indonesian_day_to_english("Rabu") == "Wednesday"
    assert indonesian_day_to_english("Kamis") == "Thursday"
    assert indonesian_day_to_english("Jumat") == "Friday"
    assert indonesian_day_to_english("Sabtu") == "Saturday"
    assert indonesian_day_to_english("Minggu") == "Sunday"
```

---

## 3. Document Structure Analysis

### Task 3.1: Section Identification and Segmentation

**Actionable Items:**
- [ ] Implement section boundary detection for Indonesian legal documents
- [ ] Create regex patterns for section headers (IDENTITAS, DAKWAAN, TUNTUTAN, etc.)
- [ ] Implement document segmentation with overlap
- [ ] Extract section content with proper boundaries
- [ ] Handle variations in section naming
- [ ] Implement subsection detection (Primair, Subsidair)
- [ ] Add section validation (ensure all required sections present)

**Positive Cases:**
- Detect all standard sections: IDENTITAS, DUDUK PERKARA, DAKWAAN, TUNTUTAN, PERTIMBANGAN, MENGADILI
- Extract section boundaries accurately
- Handle nested sections (Dakwaan Primair, Dakwaan Subsidair)
- Segment long sections with overlap
- Preserve section headers in segments

**Negative Cases:**
- Handle missing sections (some documents may not have all sections)
- Handle misspelled section headers (OCR errors)
- Handle documents with non-standard structure
- Handle very short documents

**Edge Cases:**
- Section header at page boundary
- Section with no content
- Multiple TUNTUTAN sections (amended charges)
- MENGADILI section spanning many pages
- Document with only partial structure

**Unit Tests:**
```python
def test_detect_section_boundaries():
    """Test detecting section boundaries in document"""
    text = """
    IDENTITAS
    Nama: Ahmad

    DAKWAAN
    Bahwa terdakwa...

    MENGADILI
    Menyatakan terdakwa...
    """

    sections = detect_sections(text)
    assert "IDENTITAS" in sections
    assert "DAKWAAN" in sections
    assert "MENGADILI" in sections

def test_extract_section_content():
    """Test extracting content for specific section"""
    text = load_fixture("sample_verdict.txt")

    identitas = extract_section(text, "IDENTITAS")
    assert "Nama" in identitas or "nama" in identitas

    dakwaan = extract_section(text, "DAKWAAN")
    assert "Bahwa" in dakwaan or "bahwa" in dakwaan

def test_detect_subsections():
    """Test detecting subsections in DAKWAAN"""
    dakwaan_text = """
    DAKWAAN
    PRIMAIR:
    Bahwa terdakwa...

    SUBSIDAIR:
    Bahwa terdakwa...
    """

    subsections = detect_subsections(dakwaan_text, "DAKWAAN")
    assert "PRIMAIR" in subsections
    assert "SUBSIDAIR" in subsections

def test_segment_long_section():
    """Test segmenting long section with overlap"""
    long_text = "Bahwa " * 2000  # Very long section

    segments = segment_section(
        long_text,
        max_tokens=1000,
        overlap_tokens=200
    )
    assert len(segments) > 1
    # Check overlap
    assert segments[0][-200:] in segments[1][:400]

def test_handle_missing_sections():
    """Test handling document with missing sections"""
    text = """
    IDENTITAS
    Nama: Ahmad

    MENGADILI
    Menyatakan terdakwa...
    """

    sections = detect_sections(text)
    assert "IDENTITAS" in sections
    assert "MENGADILI" in sections
    assert "DAKWAAN" not in sections  # Missing
```

---

## 4. Field Extraction - Document & Court Information

### Task 4.1: Extract Document Metadata (9 fields)

**Actionable Items:**
- [ ] Extract case_registration_number with regex + LLM
- [ ] Extract verdict_number (usually same as case_registration_number)
- [ ] Extract verdict_date from header
- [ ] Parse verdict_year from verdict_number
- [ ] Calculate verdict_day_of_week from verdict_date
- [ ] Extract court_region from case_number or document
- [ ] Map court_region to province
- [ ] Extract verdict_ruling_date from MENGADILI section
- [ ] Validate case number format

**Positive Cases:**
- Extract case number: "45/Pid.Sus-TPK/2023/PN Jkt.Pst"
- Parse verdict date: "2023-10-15"
- Extract year: 2023
- Calculate day: "Rabu"
- Extract court: "Jakarta Pusat"
- Map province: "DKI Jakarta"

**Negative Cases:**
- Handle non-standard case number format
- Handle missing verdict date
- Handle invalid date format
- Handle unknown court region

**Edge Cases:**
- Case number with unusual format
- Verdict date and ruling date different
- Court abbreviation not in mapping
- Very old case (year < 2000)

**Unit Tests:**
```python
def test_extract_case_number():
    """Test extracting case registration number"""
    text = "Nomor: 45/Pid.Sus-TPK/2023/PN Jkt.Pst"

    case_number = extract_case_number(text)
    assert case_number == "45/Pid.Sus-TPK/2023/PN Jkt.Pst"

def test_parse_year_from_case_number():
    """Test parsing year from case number"""
    case_number = "45/Pid.Sus-TPK/2023/PN Jkt.Pst"

    year = extract_year_from_case_number(case_number)
    assert year == 2023

def test_extract_court_region():
    """Test extracting court region"""
    case_number = "45/Pid.Sus-TPK/2023/PN Jkt.Pst"

    court = extract_court_region(case_number)
    assert court == "Jakarta Pusat"

def test_map_court_to_province():
    """Test mapping court region to province"""
    province = map_to_province("Jakarta Pusat")
    assert province == "DKI Jakarta"

    province = map_to_province("Surabaya")
    assert province == "Jawa Timur"

def test_calculate_day_of_week():
    """Test calculating Indonesian day of week from date"""
    day = calculate_indonesian_day("2023-10-15")
    assert day == "Minggu"  # October 15, 2023 is Sunday

def test_validate_case_number_format():
    """Test validating case number format"""
    assert validate_case_number("45/Pid.Sus-TPK/2023/PN Jkt.Pst") is True
    assert validate_case_number("invalid") is False
    assert validate_case_number("123/Pid.B/2023/PN Jakarta") is True
```

---

## 5. Field Extraction - Defendant Information

### Task 5.1: Extract Defendant Details (10 fields)

**Actionable Items:**
- [ ] Extract defendant_name from IDENTITAS section
- [ ] Extract defendant_birth_place
- [ ] Extract and parse defendant_birth_date
- [ ] Extract or calculate defendant_age
- [ ] Extract defendant_gender (Laki-laki/Perempuan)
- [ ] Extract defendant_nationality (usually Indonesia)
- [ ] Extract defendant_address
- [ ] Extract defendant_religion
- [ ] Extract defendant_occupation
- [ ] Extract defendant_education
- [ ] Validate age calculation

**Positive Cases:**
- Extract name: "AHMAD BIN HASAN"
- Extract birth place: "Jakarta"
- Parse birth date: "1985-06-15"
- Calculate age: 38
- Extract gender: "Laki-laki"
- Extract address: full address text
- Extract occupation: "Pegawai Negeri Sipil"

**Negative Cases:**
- Handle missing birth date
- Handle invalid age calculation
- Handle missing optional fields (religion, education)

**Edge Cases:**
- Name with multiple "Bin"
- Very long address (>500 characters)
- Unusual occupation description
- Age that doesn't match birth_date (use calculated)

**Unit Tests:**
```python
def test_extract_defendant_name():
    """Test extracting defendant name from IDENTITAS"""
    identitas = """
    Nama Terdakwa: AHMAD BIN HASAN
    Tempat Lahir: Jakarta
    """

    name = extract_defendant_name(identitas)
    assert name == "AHMAD BIN HASAN"
    assert "BIN" in name

def test_extract_birth_date():
    """Test extracting and parsing birth date"""
    identitas = """
    Tanggal Lahir: 15 Juni 1985
    """

    birth_date = extract_birth_date(identitas)
    assert birth_date == "1985-06-15"

def test_calculate_age():
    """Test calculating age from birth date and verdict date"""
    age = calculate_age(
        birth_date="1985-06-15",
        verdict_date="2023-10-15"
    )
    assert age == 38

def test_validate_age():
    """Test validating age calculation"""
    # Valid age
    is_valid = validate_age(
        birth_date="1985-06-15",
        verdict_date="2023-10-15",
        stated_age=38
    )
    assert is_valid is True

    # Invalid age (off by more than 1 year)
    is_valid = validate_age(
        birth_date="1985-06-15",
        verdict_date="2023-10-15",
        stated_age=35
    )
    assert is_valid is False

def test_extract_gender():
    """Test extracting gender"""
    identitas = "Jenis Kelamin: Laki-laki"

    gender = extract_gender(identitas)
    assert gender == "Laki-laki"

def test_extract_occupation():
    """Test extracting occupation"""
    identitas = "Pekerjaan: Pegawai Negeri Sipil"

    occupation = extract_occupation(identitas)
    assert occupation == "Pegawai Negeri Sipil"
```

---

## 6. Field Extraction - Pre-Trial Detention

### Task 6.1: Extract Detention Information (5 fields) with Validation

**Actionable Items:**
- [ ] Extract detention_start_date from IDENTITAS/DUDUK PERKARA
- [ ] Extract detention_end_date from IDENTITAS/AMAR
- [ ] Implement CRITICAL validation: detention_end_date d verdict_date
- [ ] Calculate detention_duration_days
- [ ] Extract detention_type (Rutan/Lapas/Tahanan Rumah)
- [ ] Extract detention_deducted boolean from MENGADILI
- [ ] Add post-processing validation and auto-adjustment

**Positive Cases:**
- Extract detention start: "2023-04-15"
- Extract detention end: "2023-10-15"
- Calculate duration: 183 days
- Extract type: "Rutan"
- Extract deducted: true
- Auto-adjust end date if > verdict date

**Negative Cases:**
- Handle missing detention dates (defendant not detained)
- Handle invalid date sequence (start > end)

**Edge Cases:**
- detention_end_date > verdict_date (MUST auto-adjust to verdict_date)
- Detention start date missing but end date present
- Detention duration = 0 (detained and released same day)
- Multiple detention periods

**Unit Tests:**
```python
def test_extract_detention_dates():
    """Test extracting detention start and end dates"""
    text = """
    Penahanan dimulai sejak tanggal 15 April 2023
    sampai dengan tanggal 15 Oktober 2023
    """

    start_date = extract_detention_start_date(text)
    end_date = extract_detention_end_date(text)

    assert start_date == "2023-04-15"
    assert end_date == "2023-10-15"

def test_detention_end_date_validation():
    """Test CRITICAL validation: detention_end_date cannot exceed verdict_date"""
    # Case 1: End date > verdict date (MUST auto-adjust)
    result = validate_and_adjust_detention_end_date(
        detention_end_date="2023-11-20",
        verdict_date="2023-10-15"
    )
    assert result["detention_end_date"] == "2023-10-15"
    assert result["adjusted"] is True
    assert "Adjusted to verdict_date" in result["note"]

    # Case 2: End date <= verdict date (no adjustment)
    result = validate_and_adjust_detention_end_date(
        detention_end_date="2023-09-15",
        verdict_date="2023-10-15"
    )
    assert result["detention_end_date"] == "2023-09-15"
    assert result["adjusted"] is False

def test_calculate_detention_duration():
    """Test calculating detention duration in days"""
    duration = calculate_detention_duration(
        start_date="2023-04-15",
        end_date="2023-10-15"
    )
    assert duration == 183

def test_extract_detention_type():
    """Test extracting detention type"""
    text = "Terdakwa ditahan di Rumah Tahanan Negara"
    dtype = extract_detention_type(text)
    assert dtype in ["Rutan", "Lapas", "Tahanan Rumah", "Tahanan Kota"]

def test_extract_detention_deducted():
    """Test extracting whether detention is deducted from sentence"""
    # Positive case
    text = "Menetapkan masa penahanan yang telah dijalani dikurangkan"
    deducted = extract_detention_deducted(text)
    assert deducted is True

    # Negative case
    text = "Menjatuhkan pidana penjara selama 5 tahun"
    deducted = extract_detention_deducted(text)
    assert deducted is False

def test_detention_date_sequence_validation():
    """Test validating detention date sequence"""
    # Valid sequence
    is_valid = validate_detention_dates(
        start_date="2023-04-15",
        end_date="2023-10-15",
        verdict_date="2023-10-15"
    )
    assert is_valid is True

    # Invalid: start > end
    is_valid = validate_detention_dates(
        start_date="2023-10-15",
        end_date="2023-04-15",
        verdict_date="2023-10-15"
    )
    assert is_valid is False
```

**Integration Test:**
```python
@pytest.mark.integration
def test_detention_extraction_with_auto_adjustment():
    """Test complete detention extraction with auto-adjustment"""
    document = load_fixture("corruption_case_sample.pdf")

    # Extract all fields
    extraction = extract_id_sc_fields(document)

    # Verify detention fields
    assert extraction["detention_start_date"] is not None
    assert extraction["detention_end_date"] is not None

    # CRITICAL: Verify auto-adjustment applied if necessary
    if extraction["detention_end_date"] > extraction["verdict_date"]:
        # This should never happen after post-processing
        pytest.fail("Detention end date exceeds verdict date - validation failed!")

    # Verify duration calculation
    expected_duration = (
        datetime.fromisoformat(extraction["detention_end_date"]) -
        datetime.fromisoformat(extraction["detention_start_date"])
    ).days
    assert extraction["detention_duration_days"] == expected_duration
```

---

## 7. Field Extraction - Legal Representatives

### Task 7.1: Extract Multi-Value Legal Representative Fields (4 fields)

**Actionable Items:**
- [ ] Extract defense_lawyer_name (can be multiple, semicolon-separated)
- [ ] Extract defense_lawyer_office_address
- [ ] Extract prosecutor_name (can be multiple, semicolon-separated)
- [ ] Extract court_clerk_name
- [ ] Extract judge_name (panel, semicolon-separated)
- [ ] Implement multi-value field parser (semicolon separator)
- [ ] Preserve professional titles (S.H., M.H.)
- [ ] Preserve commas within names

**Positive Cases:**
- Single lawyer: "Ahmad Budiman, S.H."
- Multiple lawyers: "Ahmad Budiman, S.H.; Siti Rahma, S.H., M.H."
- Multiple prosecutors: "Andi Wijaya, S.H.; Rini Susanti, S.H."
- Judge panel: "Bambang, S.H. (Ketua); Siti, S.H.; Ahmad, S.H."
- Parse and split multi-value fields correctly

**Negative Cases:**
- Handle missing defense lawyer (defendant has no lawyer)
- Handle malformed names
- Handle missing professional titles

**Edge Cases:**
- Very long list of lawyers (>5)
- Name with multiple titles: "Dr. Ahmad Budiman, S.H., M.H., Ph.D"
- Judge name with role indicator: "Bambang (Ketua Majelis)"
- Names with special characters

**Unit Tests:**
```python
def test_extract_single_lawyer():
    """Test extracting single defense lawyer"""
    text = "Penasehat Hukum: Ahmad Budiman, S.H."

    lawyers = extract_defense_lawyers(text)
    assert lawyers == "Ahmad Budiman, S.H."

def test_extract_multiple_lawyers():
    """Test extracting multiple defense lawyers"""
    text = """
    Penasehat Hukum:
    1. Ahmad Budiman, S.H.
    2. Siti Rahma, S.H., M.H.
    """

    lawyers = extract_defense_lawyers(text)
    assert lawyers == "Ahmad Budiman, S.H.; Siti Rahma, S.H., M.H."
    assert lawyers.count(";") == 1

def test_parse_multi_value_field():
    """Test parsing multi-value field with semicolon separator"""
    lawyers = "Ahmad Budiman, S.H.; Siti Rahma, S.H., M.H."

    parsed = parse_multi_value_field(lawyers)
    assert len(parsed) == 2
    assert parsed[0] == "Ahmad Budiman, S.H."
    assert parsed[1] == "Siti Rahma, S.H., M.H."

def test_preserve_commas_in_titles():
    """Test preserving commas within professional titles"""
    lawyers = "Dr. Ahmad, S.H., M.H., Ph.D; Siti, S.H."

    parsed = parse_multi_value_field(lawyers)
    assert "S.H., M.H." in parsed[0]
    assert "," in parsed[0]  # Commas within name preserved

def test_extract_judge_panel():
    """Test extracting judge panel with roles"""
    text = """
    Hakim Ketua: Dr. Bambang Sutrisno, S.H., M.H.
    Hakim Anggota: Siti Aminah, S.H.
    Hakim Anggota: Ahmad Fauzi, S.H.
    """

    judges = extract_judge_names(text)
    assert "Bambang Sutrisno" in judges
    assert judges.count(";") == 2  # 3 judges

def test_extract_prosecutors():
    """Test extracting prosecutor names"""
    text = "Jaksa Penuntut Umum: Andi Wijaya, S.H. dan Rini Susanti, S.H."

    prosecutors = extract_prosecutors(text)
    assert prosecutors == "Andi Wijaya, S.H.; Rini Susanti, S.H."

def test_handle_missing_lawyer():
    """Test handling case with no defense lawyer"""
    text = "Terdakwa tidak didampingi Penasehat Hukum"

    lawyers = extract_defense_lawyers(text)
    assert lawyers is None
```

---

## 8. Field Extraction - Charge Information

### Task 8.1: Extract Dakwaan Fields (9 fields)

**Actionable Items:**
- [ ] Extract charge_chronology (full dakwaan text)
- [ ] Extract crime_location (locus delicti)
- [ ] Extract crime_time_period (tempus delicti)
- [ ] Extract state_loss_charged (kerugian negara in Rupiah)
- [ ] Extract article_charged_first through article_charged_fourth
- [ ] Extract charge_structure_type (Alternatif/Subsidair/Kumulatif)
- [ ] Extract defense_objection (eksepsi)
- [ ] Implement legal article parser
- [ ] Handle hierarchical dakwaan structure

**Positive Cases:**
- Extract full chronology text
- Extract location: "Kantor Dinas XYZ, Jakarta"
- Extract time period: "Januari 2020 - Maret 2021"
- Extract state loss: 5000000000 (5 billion Rupiah)
- Extract articles: "Pasal 2 ayat (1)", "Pasal 3", "Pasal 18"
- Detect charge type: "Subsidair"

**Negative Cases:**
- Handle missing state loss amount
- Handle no defense objection
- Handle unclear article references

**Edge Cases:**
- Multiple state loss amounts (use primary)
- >4 articles charged (extract first 4)
- Very long chronology (>50KB)
- Approximate time period (only year)

**Unit Tests:**
```python
def test_extract_crime_location():
    """Test extracting locus delicti"""
    dakwaan = "Perbuatan dilakukan di Kantor Dinas Pekerjaan Umum, Jakarta"

    location = extract_crime_location(dakwaan)
    assert "Jakarta" in location

def test_extract_crime_time_period():
    """Test extracting tempus delicti"""
    dakwaan = "Perbuatan dilakukan pada periode Januari 2020 sampai Maret 2021"

    period = extract_crime_time_period(dakwaan)
    assert period == "Januari 2020 - Maret 2021"

def test_extract_state_loss():
    """Test extracting state loss amount"""
    dakwaan = "Kerugian negara sebesar Rp. 5.000.000.000,-"

    loss = extract_state_loss(dakwaan)
    assert loss == 5000000000

def test_extract_legal_articles():
    """Test extracting legal article references"""
    dakwaan = """
    melanggar Pasal 2 ayat (1) jo. Pasal 18
    UU No. 31 Tahun 1999 jo. UU No. 20 Tahun 2001
    """

    articles = extract_articles(dakwaan)
    assert "Pasal 2 ayat (1)" in articles
    assert "Pasal 18" in articles

def test_detect_charge_structure():
    """Test detecting dakwaan structure type"""
    # Subsidair structure
    dakwaan_subsidair = """
    PRIMAIR:
    Bahwa terdakwa...
    SUBSIDAIR:
    Bahwa terdakwa...
    """
    assert detect_charge_structure(dakwaan_subsidair) == "Subsidair"

    # Alternatif structure
    dakwaan_alternatif = """
    KESATU:
    ATAU
    KEDUA:
    """
    assert detect_charge_structure(dakwaan_alternatif) == "Alternatif"

def test_extract_defense_objection():
    """Test extracting defense objection"""
    text = """
    EKSEPSI:
    Penasehat Hukum mengajukan keberatan terhadap dakwaan...
    """

    objection = extract_defense_objection(text)
    assert "keberatan" in objection.lower()
```

---

## 9. Field Extraction - Financial & Corruption Details

### Task 9.1: Extract Financial Fields (9 fields)

**Actionable Items:**
- [ ] Extract prosecution_restitution_demand (uang pengganti tuntutan)
- [ ] Extract verdict_restitution_amount (uang pengganti amar)
- [ ] Extract state_loss_recovered (pengembalian kerugian negara)
- [ ] Extract corruption_proceeds (uang korupsi yang diperoleh)
- [ ] Calculate remaining_restitution (verdict_restitution - state_loss_recovered)
- [ ] Extract state_loss_verdict (kerugian negara menurut pengadilan)
- [ ] Extract state_loss_auditor (BPKP/BPK/Inspektorat)
- [ ] Extract prosecution_fine_demand
- [ ] Extract verdict_fine_amount
- [ ] Validate all amounts as BIGINT (handle billions of Rupiah)

**Positive Cases:**
- Extract restitution demand: 3500000000
- Extract restitution verdict: 2500000000
- Extract state loss recovered: 500000000
- Calculate remaining: 2000000000
- Extract auditor: "BPKP"
- Handle amounts >1 trillion Rupiah

**Negative Cases:**
- Handle missing financial amounts
- Handle partial recovery (some fields null)

**Edge Cases:**
- Zero restitution (no financial penalty)
- Full recovery (remaining = 0)
- Amount in text format: "dua setengah miliar"
- Multiple auditor mentions (use first)

**Unit Tests:**
```python
def test_extract_restitution_amount():
    """Test extracting restitution amounts"""
    tuntutan = "membayar uang pengganti sebesar Rp. 3.500.000.000,-"
    amount = extract_restitution_demand(tuntutan)
    assert amount == 3500000000

    amar = "membayar uang pengganti sebesar Rp. 2.500.000.000,-"
    amount = extract_restitution_verdict(amar)
    assert amount == 2500000000

def test_extract_state_loss_recovered():
    """Test extracting recovered state loss"""
    text = "Terdakwa telah mengembalikan kerugian negara sebesar Rp. 500.000.000,-"

    recovered = extract_state_loss_recovered(text)
    assert recovered == 500000000

def test_calculate_remaining_restitution():
    """Test calculating remaining restitution"""
    remaining = calculate_remaining_restitution(
        verdict_restitution=2500000000,
        state_loss_recovered=500000000
    )
    assert remaining == 2000000000

def test_extract_auditor():
    """Test extracting state loss auditor"""
    text = "Berdasarkan laporan BPKP, kerugian negara sebesar..."

    auditor = extract_state_loss_auditor(text)
    assert auditor == "BPKP"

def test_handle_trillion_rupiah():
    """Test handling amounts in trillions"""
    text = "kerugian negara sebesar Rp. 1.500.000.000.000,-"

    amount = extract_state_loss(text)
    assert amount == 1500000000000  # 1.5 trillion

def test_parse_text_amount():
    """Test parsing text currency amounts"""
    amount = parse_indonesian_currency_text("dua miliar lima ratus juta rupiah")
    assert amount == 2500000000
```

---

## 10. Field Extraction - Mitigating & Aggravating Factors

### Task 10.1: Extract Sentencing Considerations (10 fields)

**Actionable Items:**
- [ ] Extract aggravating_factor_1 through aggravating_factor_5
- [ ] Extract mitigating_factor_1 through mitigating_factor_7
- [ ] Extract factors in order as they appear in PERTIMBANGAN
- [ ] Handle variable number of factors (some may be null)
- [ ] Extract as direct quotes where possible
- [ ] Identify factor category (memberatkan vs meringankan)

**Positive Cases:**
- Extract 2-3 aggravating factors
- Extract 3-5 mitigating factors
- Preserve exact wording from document
- Handle Indonesian legal phrases
- Extract in correct order

**Negative Cases:**
- Handle documents with no explicit factors
- Handle very brief factor descriptions

**Edge Cases:**
- 7+ mitigating factors (extract first 7)
- Factors stated as bullet points
- Factors in narrative format
- Duplicate factors mentioned

**Unit Tests:**
```python
def test_extract_aggravating_factors():
    """Test extracting aggravating factors"""
    pertimbangan = """
    Hal-hal yang memberatkan:
    - Perbuatan terdakwa merugikan keuangan negara
    - Tidak mendukung program pemberantasan korupsi
    """

    factors = extract_aggravating_factors(pertimbangan)
    assert len(factors) >= 2
    assert "merugikan keuangan negara" in factors[0]

def test_extract_mitigating_factors():
    """Test extracting mitigating factors"""
    pertimbangan = """
    Hal-hal yang meringankan:
    - Terdakwa bersikap sopan di persidangan
    - Terdakwa belum pernah dihukum
    - Terdakwa menyesali perbuatannya
    - Terdakwa memiliki tanggungan keluarga
    """

    factors = extract_mitigating_factors(pertimbangan)
    assert len(factors) >= 4
    assert "sopan" in factors[0]

def test_handle_missing_factors():
    """Test handling document with no explicit factors"""
    pertimbangan = "Majelis Hakim mempertimbangkan..."

    aggravating = extract_aggravating_factors(pertimbangan)
    mitigating = extract_mitigating_factors(pertimbangan)

    # Should return empty list or nulls
    assert aggravating is None or len(aggravating) == 0

def test_preserve_factor_order():
    """Test preserving factor order as they appear"""
    pertimbangan = """
    Hal-hal yang meringankan:
    - Faktor pertama
    - Faktor kedua
    - Faktor ketiga
    """

    factors = extract_mitigating_factors(pertimbangan)
    assert "pertama" in factors[0]
    assert "kedua" in factors[1]
    assert "ketiga" in factors[2]
```

---

## 11. Complete Document Extraction

### Task 11.1: Multi-Pass Extraction Pipeline

**Actionable Items:**
- [ ] Implement Pass 1: Quick scan with Gemini Flash
- [ ] Implement Pass 2: Detailed extraction with Gemini Pro
- [ ] Implement Pass 3: Validation pass
- [ ] Implement conditional Pass 4: Deep dive for low confidence
- [ ] Aggregate results from multiple passes
- [ ] Select best extraction for each field
- [ ] Calculate overall confidence score
- [ ] Track cost per pass

**Positive Cases:**
- Complete all 4 passes successfully
- Extract all 77 fields
- Select best value for each field
- Overall confidence >85%
- Total cost <$2

**Negative Cases:**
- Handle pass failure (retry)
- Handle timeout
- Handle low confidence fields

**Edge Cases:**
- Skip Pass 4 if all fields high confidence
- Conflicting values between passes
- Cost approaching budget limit

**Integration Test:**
```python
@pytest.mark.integration
def test_complete_id_sc_extraction():
    """Test complete extraction of all 77 fields"""
    document_path = "tests/fixtures/corruption_case_full.pdf"

    # Run extraction
    result = extract_id_sc_document(document_path)

    # Verify all critical fields extracted
    assert result["case_registration_number"] is not None
    assert result["verdict_date"] is not None
    assert result["defendant_name"] is not None
    assert result["verdict_prison_total_months"] is not None

    # Verify detention validation applied
    if result["detention_end_date"] and result["verdict_date"]:
        assert result["detention_end_date"] <= result["verdict_date"]

    # Verify multi-value fields
    if result["defense_lawyer_name"]:
        assert isinstance(result["defense_lawyer_name"], str)

    # Verify financial fields as BIGINT
    if result["verdict_restitution_amount"]:
        assert isinstance(result["verdict_restitution_amount"], int)
        assert result["verdict_restitution_amount"] > 0

    # Verify cost within budget
    assert result["total_cost"] < 2.00

    # Verify confidence
    assert result["overall_confidence"] > 0.80

    # Count fields extracted
    fields_extracted = sum(1 for v in result.values() if v is not None)
    assert fields_extracted >= 50  # At least 50 of 77 fields
```

---

## 12. Validation Rules

### Task 12.1: Implement All Validation Rules

**Actionable Items:**
- [ ] Implement detention date validation (CRITICAL)
- [ ] Implement date sequence validation
- [ ] Implement age calculation validation
- [ ] Implement case number format validation
- [ ] Implement currency amount validation (non-negative)
- [ ] Implement cross-field consistency checks
- [ ] Implement legal article format validation
- [ ] Generate validation reports

**Positive Cases:**
- All validations pass
- Auto-adjustment applied successfully
- Validation warnings logged

**Negative Cases:**
- Validation failure (flag for review)
- Inconsistent cross-field data

**Unit Tests:**
```python
def test_detention_date_validation_rule():
    """Test the CRITICAL detention date validation rule"""
    validation_result = validate_detention_dates(
        detention_start_date="2020-03-15",
        detention_end_date="2023-11-20",
        verdict_date="2023-10-15"
    )

    assert validation_result["valid"] is False
    assert "exceeds verdict_date" in validation_result["message"]

    # Auto-adjust
    adjusted = auto_adjust_detention_end_date(
        detention_end_date="2023-11-20",
        verdict_date="2023-10-15"
    )
    assert adjusted == "2023-10-15"

def test_date_sequence_validation():
    """Test date sequence validation"""
    is_valid = validate_date_sequence(
        detention_start_date="2023-01-15",
        detention_end_date="2023-10-15",
        verdict_date="2023-10-15"
    )
    assert is_valid is True

def test_cross_field_validation():
    """Test cross-field consistency validation"""
    validation = validate_cross_fields(
        state_loss_charged=5000000000,
        state_loss_verdict=2500000000,
        verdict_restitution_amount=2500000000
    )
    # Verdict should not exceed charged amount
    assert validation["valid"] is True
```

---

## Summary

**Total ID_SC Tasks:** 12 major tasks

**Field Coverage:**
- Document & Court Information: 9 fields
- Defendant Information: 10 fields
- Pre-Trial Detention: 5 fields (with CRITICAL validation)
- Legal Representatives: 4 fields (multi-value support)
- Charge Information: 9 fields
- Prosecution Demands: 7 fields
- Verdict Information: 16 fields
- Financial & Corruption: 9 fields
- Sentencing Factors: 10 fields
**Total:** 77 fields + 2 derived fields

**Critical Features:**
1.  Detention date validation and auto-adjustment
2.  Multi-value field support with semicolon separator
3.  Indonesian language processing
4.  BIGINT financial amounts (billions of Rupiah)
5.  Complex document structure handling

**Testing Strategy:**
- Unit tests for each field extraction function
- Integration tests for complete document extraction
- Edge case coverage >90%
- Cost tracking and budget validation

**Success Criteria:**
- Extract all 77 fields with >85% accuracy
- Complete extraction in <5 minutes
- Total cost <$2 per document
- Detention validation 100% accurate
- Multi-value fields parsed correctly
