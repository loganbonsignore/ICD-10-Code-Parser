# ICD-10 Code Parser

### Project Overview
This project parses XML documents containing ICD-10 medical codes provided by the Center for Medicare & Medicaid Services (CMS). The codes are converted from XML format to JSON format. All possible code combinations are calculated using the official guidelines of coding and reporting.

### Tools Used
Python and the ElementTree XML library.

### Data Sources
Official ICD-10 XML files are downloaded from [cms.gov](https://www.cms.gov/Medicare/Coding/ICD10).
The notebook _parse.ipynb_ is built to parse _icd10pcs_tables_2020.xml_.
